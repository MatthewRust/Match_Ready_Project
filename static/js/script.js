function showHomeMatches(){
    var homeDiv = document.getElementById("home_matches");
    var awayDiv = document.getElementById("away_matches");
    homeDiv.style.display="block"
    awayDiv.style.display="none"
}

function showAwayMatches(){
    var homeDiv = document.getElementById("home_matches");
    var awayDiv = document.getElementById("away_matches");
    homeDiv.style.display="none"
    awayDiv.style.display="block"
}

document.addEventListener("DOMContentLoaded", function() {
    var homeButton = document.getElementById("home_matches_button");
    homeButton.addEventListener("click", showHomeMatches);

    var awayButton = document.getElementById("away_matches_button");
    awayButton.addEventListener("click", showAwayMatches);
});