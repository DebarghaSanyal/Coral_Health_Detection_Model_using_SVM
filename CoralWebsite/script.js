async function checkCoral() {
    const fileInput = document.getElementById('coralImage');
    const resultDiv = document.getElementById('result');
    const imagePreview = document.getElementById('uploadedImage');
    const pieChartDiv = document.getElementById('pieChart');

    if (!fileInput.files[0]) {
        resultDiv.innerText = "Please upload an image!";
        return;
    }

    const formData = new FormData();
    formData.append('image', fileInput.files[0]);

    resultDiv.innerText = "Analyzing...";

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();

        // Show prediction result
        resultDiv.innerText = `The coral is ${data.prediction}!`;

        // Show uploaded image
        const img = document.createElement('img');
        img.src = URL.createObjectURL(fileInput.files[0]);
        img.style.maxWidth = "300px"; // Adjust image size
        imagePreview.innerHTML = '';
        imagePreview.appendChild(img);

        // Get the prediction confidence (assumed response format)
        let healthyPercentage = data.healthy_percentage.toFixed(2) || 80; // Default if not provided
        let bleachedPercentage = 100 - healthyPercentage;        

        
        // Clear previous chart
        pieChartDiv.innerHTML = '<canvas id="coralChart"></canvas>';

        // Draw pie chart using Chart.js
        const ctx = document.getElementById('coralChart').getContext('2d');
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['Healthy', 'Bleached'],
                datasets: [{
                    data: [healthyPercentage, bleachedPercentage],
                    backgroundColor: ['#1D84B5', '#EC4067']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });

    } catch (error) {
        resultDiv.innerText = "Error analyzing the image.";
        imagePreview.innerHTML = '';
        pieChartDiv.innerHTML = '';
        console.error("Error:", error);
    }
}
