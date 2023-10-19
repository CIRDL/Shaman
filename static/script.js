document.addEventListener("DOMContentLoaded", function() {
    // Get references to the HTML elements
    const majorDropdown = document.getElementById("major-types");
    const semestersInput = document.getElementById("semesters");
    const goButton = document.getElementById("run-algorithm");

    goButton.addEventListener("click", function() {
        const selectedMajor = majorDropdown.value;
        const numSemesters = semestersInput.value;

        // You can then send these values to your Python backend using AJAX (like using the Fetch API)
        fetch("/generate-schedule", {
            method: 'POST',
            method: 'GET',
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                major: selectedMajor,
                semesters: numSemesters,
            }),
        })
        .then(response => response.json())
        .then(data => {
            // Process the data returned from your Python backend
            console.log(data);
        })
        .catch(error => {
            console.error("Error:", error);
        });
    });
});
