function loadWeather(place) {
    fetch(`/weather/${place}`)
        .then(response => response.json())
        .then(data => {
            console.log(data);
            document.getElementById("temp").innerText = data.main.temp + "°C";
            document.getElementById("condition").innerText = data.weather[0].description;
            document.getElementById("humidity").innerText = data.main.humidity + "%";
            //Lines above tell the software which weather data we want to pull from the API


            const lat = data.coord.lat;
            const lon = data.coord.lon;

            if (!lat || !lon) {
                console.error("Coordinates missing!");
                return;
            }


            // Creates a map container dynamically
            const mapContainer = document.getElementById("map");
            mapContainer.innerHTML = "";
            window.myMap = L.map("map").setView([lat, lon], 13);

            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; OpenStreetMap contributors'
            }).addTo(window.myMap);

            L.marker([lat, lon]).addTo(window.myMap)
                .bindPopup(`${data.name}`)
                .openPopup();
        })
        .catch(err => console.error(err));

}
