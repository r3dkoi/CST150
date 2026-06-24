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
let menu = document.getElementById("changeText");
let text = document.getElementById("text");

menu.addEventListener("click", function() {
    text.textContent = "You clicked the button!";
    text.classList.toggle('text_colour_toggle');
});

//Toggleable navigation 
let nav_button = document.getElementById("hamburger_menu")
let navigation_menu = document.getElementById("links")

nav_button.addEventListener("click", function() {
    navigation_menu.classList.toggle('collapsible');
})