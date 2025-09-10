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

        # ------------------------------------------
        # 📌 Parâmetros de filtro da URL
        # ------------------------------------------
        today = date.today()
        selected_year = int(self.request.GET.get("year", today.year))
        selected_month = int(self.request.GET.get("month", today.month))
        selected_seller = self.request.GET.get("seller")
        selected_status = self.request.GET.get("status", "ALL")  # ALL, PAID, PENDING

        # ------------------------------------------
        # 📌 Cálculo do mês anterior
        # ------------------------------------------
        prev_month = 12 if selected_month == 1 else selected_month - 1
        prev_year = selected_year - 1 if selected_month == 1 else selected_year

        # ------------------------------------------
        # 📌 Querysets base (vendas e comissões)
        # ------------------------------------------
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

        # ------------------------------------------
        # 📌 Aplicação de filtros por usuário/permissão
        # ------------------------------------------
        if is_vendedor(user):
            # Vendedor vê apenas seus próprios dados
            sales_qs = sales_qs.filter(seller=user)
            sales_prev_month_qs = sales_prev_month_qs.filter(seller=user)
            reports_qs = reports_qs.filter(seller=user)

        elif selected_seller and selected_seller.isdigit():
            # Admin ou gestor filtrando por vendedor específico
            sales_qs = sales_qs.filter(seller_id=selected_seller)
            sales_prev_month_qs = sales_prev_month_qs.filter(seller_id=selected_seller)
            reports_qs = reports_qs.filter(seller_id=selected_seller)

        # Filtro por status da comissão
        if selected_status != "ALL":
            reports_qs = reports_qs.filter(status=selected_status)

        # ------------------------------------------
        # 📌 Cálculo de totais
        # ------------------------------------------
        total_sales = sales_qs.aggregate(total=Sum("total_amount"))["total"] or Decimal("0.00")
        total_commissions = reports_qs.aggregate(total=Sum("total_commission"))["total"] or Decimal("0.00")
        paid_commissions = reports_qs.filter(status="PAID").aggregate(
            total=Sum("total_commission")
        )["total"] or Decimal("0.00")

        prev_total_sales = sales_prev_month_qs.aggregate(
            total=Sum("total_amount")
        )["total"] or Decimal("0.00")

        # Crescimento das vendas em relação ao mês anterior
        sales_growth = (
            ((total_sales - prev_total_sales) / prev_total_sales) * 100
            if prev_total_sales > 0 else 0
        )

        # ------------------------------------------
        # 📌 Dados para filtros e exibição
        # ------------------------------------------
        context.update({
            "total_sales": total_sales,
            "total_commissions": total_commissions,
            "paid_commissions": paid_commissions,
            "pending_commissions": total_commissions - paid_commissions,
            "sales_growth": round(sales_growth, 2),
            "selected_year": selected_year,
            "selected_month": selected_month,
            "selected_seller": int(selected_seller) if selected_seller and selected_seller.isdigit() else None,
            "selected_status": selected_status,
            "years": range(today.year, today.year - 5, -1),
            "months": [
                {"num": i, "name": date(2000, i, 1).strftime("%B")}
                for i in range(1, 13)
            ],
            "sellers": Account.objects.filter(is_active=True, is_staff=False).order_by("first_name"),
        })

        # ------------------------------------------
        # 📊 Dados do gráfico diário de vendas
        # ------------------------------------------
        sales_by_day = (
            sales_qs.annotate(day=TruncDay("sale_date"))
            .values("day")
            .annotate(total_day=Sum("total_amount"))
            .order_by("day")
        )

        context["chart_labels"] = json.dumps([s["day"].strftime("%d/%m") for s in sales_by_day])
        context["chart_data"] = json.dumps([float(s["total_day"]) for s in sales_by_day])

        # ------------------------------------------
        # 🏆 Ranking dos Top 5 Vendedores (admin only)
        # ------------------------------------------
        if is_administrador(user):
            top_sellers_qs = (
                sales_qs.values("seller__first_name", "seller__last_name", "seller__username")
                .annotate(total_sales_seller=Sum("total_amount"))
                .order_by("-total_sales_seller")[:5]
            )

            top_sellers = []
            if top_sellers_qs.exists():
                max_sales = top_sellers_qs[0]["total_sales_seller"] or Decimal("0.00")
                for seller in top_sellers_qs:
                    seller["progress_percentage"] = int(
                        (seller["total_sales_seller"] / max_sales * 100) if max_sales > 0 else 0
                    )
                    top_sellers.append(seller)

            context["top_sellers"] = top_sellers

        return context


class VendedorDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/vendedor_dashboard.html'
    # Esta view pode ser expandida com funcionalidades específicas para vendedores
    # Por enquanto, redireciona para a view principal do dashboard
    def get(self, request, *args, **kwargs):
        return DashboardView.as_view()(request, *args, **kwargs)
    