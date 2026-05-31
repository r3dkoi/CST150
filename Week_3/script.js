// Variables & Data Types
let message = "Hello, JavaScript!";
console.log(message);

//function declaration
function greetUser() {
    alert("Welcome to JavaScript Fundamentals!");
}

//Calls function when page loads
document.addEventListener("DOMContentLoaded", greetUser);

//DOM Manipulation
let button = document.getElementById("changeText");
let text = document.getElementById("text");

button.addEventListener("click", function() {
    text.textContent = "You clicked the button!";
    text.style.color = "green";
})