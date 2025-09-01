# apps/dashboard/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models import Sum
from django.db.models.functions import TruncDay
from datetime import date
from decimal import Decimal
import json

from apps.sales.models import DailySales
from apps.commissions.models import MonthlyCommissionReport
from apps.accounts.models import Account
from apps.accounts.utils import is_administrador, is_vendedor


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # ------------------------------
        # 📌 FILTROS vindos da URL
        # ------------------------------
        selected_year = int(self.request.GET.get("year", date.today().year))
        selected_month = int(self.request.GET.get("month", date.today().month))
        selected_seller = self.request.GET.get("seller")
        selected_status = self.request.GET.get("status")  # PAID / PENDING / ALL

        # ------------------------------
        # 📌 Mês anterior
        # ------------------------------
        prev_month = selected_month - 1 or 12
        prev_year = selected_year if selected_month != 1 else selected_year - 1

        # ------------------------------
        # 📌 Querysets base
        # ------------------------------
        sales_qs = DailySales.objects.filter(
            sale_date__year=selected_year,
            sale_date__month=selected_month,
            is_active=True,
        )
        sales_prev_month_qs = DailySales.objects.filter(
            sale_date__year=prev_year,
            sale_date__month=prev_month,
            is_active=True,
        )
        reports_qs = MonthlyCommissionReport.objects.filter(
            year=selected_year,
            month=selected_month,
        )

        # ------------------------------
        # 📌 Regras de permissão
        # ------------------------------
        if is_vendedor(user):
            sales_qs = sales_qs.filter(seller=user)
            sales_prev_month_qs = sales_prev_month_qs.filter(seller=user)
            reports_qs = reports_qs.filter(seller=user)
        else:
            # Se for admin → pode filtrar por vendedor
            if selected_seller and selected_seller.isdigit():
                sales_qs = sales_qs.filter(seller_id=selected_seller)
                sales_prev_month_qs = sales_prev_month_qs.filter(seller_id=selected_seller)
                reports_qs = reports_qs.filter(seller_id=selected_seller)

        # Filtro por status de comissão
        if selected_status and selected_status != "ALL":
            reports_qs = reports_qs.filter(status=selected_status)

        # ------------------------------
        # 📌 Cálculos principais
        # ------------------------------
        total_sales = sales_qs.aggregate(total=Sum("total_amount"))["total"] or Decimal("0.00")
        total_commissions = reports_qs.aggregate(total=Sum("total_commission"))["total"] or Decimal("0.00")
        paid_commissions = (
            reports_qs.filter(status="PAID").aggregate(total=Sum("total_commission"))["total"]
            or Decimal("0.00")
        )
        prev_total_sales = (
            sales_prev_month_qs.aggregate(total=Sum("total_amount"))["total"] or Decimal("0.00")
        )

        sales_growth = (
            (total_sales - prev_total_sales) / prev_total_sales * 100
            if prev_total_sales > 0
            else 0
        )

        context.update(
            {
                "total_sales": float(total_sales),
                "total_commissions": float(total_commissions),
                "paid_commissions": float(paid_commissions),
                "pending_commissions": float(total_commissions - paid_commissions),
                "sales_growth": round(sales_growth, 2),
                "selected_year": selected_year,
                "selected_month": selected_month,
                "selected_seller": int(selected_seller) if selected_seller and selected_seller.isdigit() else None,
                "selected_status": selected_status or "ALL",
                "years": range(date.today().year, date.today().year - 5, -1),
                "months": [
                    {"num": i, "name": date(2000, i, 1).strftime("%B")}
                    for i in range(1, 13)
                ],
                "sellers": Account.objects.filter(is_active=True, is_staff=False).order_by("first_name"),
            }
        )

        # ------------------------------
        # 📌 Gráfico diário
        # ------------------------------
        sales_by_day = (
            sales_qs.annotate(day=TruncDay("sale_date"))
            .values("day")
            .annotate(total_day=Sum("total_amount"))
            .order_by("day")
        )
        chart_labels = [s["day"].strftime("%d/%m") for s in sales_by_day]
        chart_data = [float(s["total_day"]) for s in sales_by_day]

        context["chart_labels"] = json.dumps(chart_labels)
        context["chart_data"] = json.dumps(chart_data)

        # ------------------------------
        # 📌 Ranking de vendedores
        # ------------------------------
        top_sellers_qs = (
            sales_qs.values("seller__first_name", "seller__last_name", "seller__username")
            .annotate(total_sales_seller=Sum("total_amount"))
            .order_by("-total_sales_seller")[:5]
        )

        top_sellers = []
        if top_sellers_qs.exists():
            max_sales = top_sellers_qs[0]["total_sales_seller"] or 0
            for seller in top_sellers_qs:
                progress = int(
                    (seller["total_sales_seller"] / max_sales * 100) if max_sales > 0 else 0
                )
                seller["progress_percentage"] = progress
                top_sellers.append(seller)

        context["top_sellers"] = top_sellers

        return context
