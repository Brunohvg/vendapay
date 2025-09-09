// JavaScript para o formulário de múltiplos passos

let currentStep = 1;
const totalSteps = 4;

function updateStepProgress() {
    // Atualizar barra de progresso
    const progressBar = document.getElementById('progressBar');
    const progressPercentage = ((currentStep - 1) / (totalSteps - 1)) * 100;
    progressBar.style.width = progressPercentage + '%';

    // Atualizar círculos dos passos
    for (let i = 1; i <= totalSteps; i++) {
        const circle = document.getElementById(`step-circle-${i}`);
        const stepItem = document.querySelector(`[data-step="${i}"]`);
        const label = stepItem.querySelector('.step-label');

        circle.classList.remove('active', 'completed');
        label.classList.remove('active');

        if (i < currentStep) {
            circle.classList.add('completed');
            circle.innerHTML = '<i class="ti ti-check"></i>';
        } else if (i === currentStep) {
            circle.classList.add('active');
            label.classList.add('active');
            // Restaurar ícone original
            const icons = ['ti-user', 'ti-address-book', 'ti-key', 'ti-settings'];
            circle.innerHTML = `<i class="ti ${icons[i - 1]}"></i>`;
        } else {
            // Restaurar ícone original para passos futuros
            const icons = ['ti-user', 'ti-address-book', 'ti-key', 'ti-settings'];
            circle.innerHTML = `<i class="ti ${icons[i - 1]}"></i>`;
        }
    }

    // Mostrar/esconder conteúdo dos passos
    document.querySelectorAll('.step-content').forEach((content, index) => {
        if (index + 1 === currentStep) {
            content.classList.add('active');
        } else {
            content.classList.remove('active');
        }
    });

    // Atualizar botões
    document.getElementById('prevBtn').style.display = currentStep > 1 ? 'block' : 'none';
    document.getElementById('nextBtn').style.display = currentStep < totalSteps ? 'block' : 'none';
    document.getElementById('submitBtn').style.display = currentStep === totalSteps ? 'block' : 'none';

    // Atualizar informação do passo
    document.getElementById('step-info').textContent = `Passo ${currentStep} de ${totalSteps}`;
}

function validateStep(step) {
    const stepElement = document.getElementById(`step-${step}`);
    const requiredFields = stepElement.querySelectorAll('[required]');
    let isValid = true;

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });

    return isValid;
}

function changeStep(direction) {
    // Se estamos avançando, validar o passo atual
    if (direction > 0 && !validateStep(currentStep)) {
        return;
    }

    const newStep = currentStep + direction;

    if (newStep >= 1 && newStep <= totalSteps) {
        currentStep = newStep;
        updateStepProgress();
    }
}

// Verificador de força da senha
document.getElementById('password').addEventListener('input', function () {
    const password = this.value;
    const strengthBar = document.getElementById('passwordStrengthBar');

    if (password.length === 0) {
        strengthBar.className = 'password-strength-bar';
        return;
    }

    let strength = 0;
    if (password.length >= 8) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^A-Za-z0-9]/.test(password)) strength++;

    strengthBar.classList.remove('weak', 'medium', 'strong');
    if (strength < 2) {
        strengthBar.classList.add('weak');
    } else if (strength < 4) {
        strengthBar.classList.add('medium');
    } else {
        strengthBar.classList.add('strong');
    }
});

// Submissão do formulário
document.getElementById('userForm').addEventListener('submit', function (e) {
    e.preventDefault();

    // Validar todos os passos
    let allValid = true;
    for (let i = 1; i <= totalSteps; i++) {
        if (!validateStep(i)) {
            allValid = false;
            // Ir para o primeiro passo com erro
            currentStep = i;
            updateStepProgress();
            break;
        }
    }

    if (allValid) {
        alert('Usuário salvo com sucesso!');
        // Aqui você pode enviar os dados para o servidor
        // location.reload(); // ou fechar o modal
    }
});

// Permitir navegação por teclado
document.addEventListener('keydown', function (e) {
    const modal = document.getElementById('userFormModal');
    if (modal.classList.contains('show')) {
        if (e.key === 'ArrowLeft' && currentStep > 1) {
            changeStep(-1);
        } else if (e.key === 'ArrowRight' && currentStep < totalSteps) {
            changeStep(1);
        }
    }
});

// Reinicializar modal quando aberto
document.getElementById('userFormModal').addEventListener('show.bs.modal', function () {
    currentStep = 1;
    updateStepProgress();
    document.getElementById('userForm').reset();
    document.querySelectorAll('.is-invalid').forEach(field => {
        field.classList.remove('is-invalid');
    });
});
