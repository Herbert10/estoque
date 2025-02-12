document.addEventListener("DOMContentLoaded", function () {
    const boxes = document.querySelectorAll('.box');

    // Função para atualizar as cores do semáforo com base no valor
    function updateSemaphores() {
        boxes.forEach(box => {
            const valueElement = box.querySelector('.value');
            const value = parseInt(valueElement.textContent.trim());
            const lights = box.querySelectorAll('.light');

            lights.forEach(light => light.classList.remove('active'));

            if (value >= 0 && value <= 5) {
                lights[2].classList.add('active'); // Verde
            } else if (value >= 6 && value <= 10) {
                lights[1].classList.add('active'); // Amarelo
            } else {
                lights[0].classList.add('active'); // Vermelho
            }
        });
    }

    // Função para buscar dados atualizados do servidor
    function fetchUpdatedData() {
        fetch("/api/data")
            .then(response => response.json())
            .then(data => {
                // Atualizar valores na página
                boxes.forEach(box => {
                    const status = box.dataset.status; // Identifica o status do card
                    const valueElement = box.querySelector('.value');
                    if (status in data) {
                        valueElement.textContent = data[status]; // Atualiza o valor
                    } else {
                        valueElement.textContent = 0; // Define valor padrão como 0
                    }
                });

                // Atualizar semáforos após mudar os valores
                updateSemaphores();
            })
            .catch(error => console.error("Erro ao buscar os dados:", error));
    }

    // Atualiza os dados imediatamente ao carregar e a cada 20 segundos
    fetchUpdatedData();
    setInterval(fetchUpdatedData, 20000);
});
