// ============================================================
// MOBILE NAVIGATION
// ============================================================

function toggleMenu() {
    const nav = document.querySelector(".nav-links");

    if (nav) {
        nav.classList.toggle("show");
    }
}


// ============================================================
// PASSWORD SHOW / HIDE
// ============================================================

function togglePassword(id) {
    const input = document.getElementById(id);

    if (!input) {
        return;
    }

    if (input.type === "password") {
        input.type = "text";
    } else {
        input.type = "password";
    }
}


// ============================================================
// LOGIN FORM VALIDATION
// ============================================================

function validateForm() {
    const email = document.getElementById("email");
    const password = document.getElementById("password");

    if (!email || !password) {
        return true;
    }

    if (email.value.trim() === "") {
        alert("Email is required.");
        email.focus();
        return false;
    }

    if (password.value.length < 8) {
        alert("Password must contain at least 8 characters.");
        password.focus();
        return false;
    }

    return true;
}


// ============================================================
// REGISTER FORM VALIDATION
// ============================================================

function validateRegisterForm() {
    const name = document.getElementById("name");
    const email = document.getElementById("email");
    const password = document.getElementById("password");
    const confirmPassword =
        document.getElementById("confirm_password");

    if (!name || !email || !password || !confirmPassword) {
        return true;
    }

    if (name.value.trim() === "") {
        alert("Name is required.");
        name.focus();
        return false;
    }

    if (email.value.trim() === "") {
        alert("Email is required.");
        email.focus();
        return false;
    }

    if (password.value.length < 8) {
        alert("Password must contain at least 8 characters.");
        password.focus();
        return false;
    }

    if (password.value !== confirmPassword.value) {
        alert("Passwords do not match.");
        confirmPassword.focus();
        return false;
    }

    return true;
}


// ============================================================
// LOST / FOUND ITEM FORM VALIDATION
// ============================================================

function validateItemForm() {
    const item = document.getElementById("item_name");
    const location = document.getElementById("location");
    const category = document.getElementById("category");

    if (item && item.value.trim() === "") {
        alert("Enter item name.");
        item.focus();
        return false;
    }

    if (category && category.value.trim() === "") {
        alert("Select a category.");
        category.focus();
        return false;
    }

    if (location && location.value.trim() === "") {
        alert("Enter location.");
        location.focus();
        return false;
    }

    return true;
}


// ============================================================
// IMAGE PREVIEW
// ============================================================

function previewImage(event) {
    const preview = document.getElementById("preview");

    if (!preview) {
        return;
    }

    const file = event.target.files[0];

    if (!file) {
        preview.style.display = "none";
        return;
    }

    const allowedTypes = [
        "image/png",
        "image/jpeg",
        "image/gif",
        "image/webp"
    ];

    if (!allowedTypes.includes(file.type)) {
        alert("Please select a valid image file.");
        event.target.value = "";
        preview.style.display = "none";
        return;
    }

    // Maximum 5 MB
    const maxSize = 5 * 1024 * 1024;

    if (file.size > maxSize) {
        alert("Image size must be less than 5 MB.");
        event.target.value = "";
        preview.style.display = "none";
        return;
    }

    preview.src = URL.createObjectURL(file);
    preview.style.display = "block";
}


// ============================================================
// LOGOUT CONFIRMATION
// ============================================================

function confirmLogout() {
    return confirm(
        "Are you sure you want to logout?"
    );
}


// ============================================================
// SUCCESS MESSAGE
// ============================================================

function showSuccess(message) {
    alert(message);
}


// ============================================================
// AUTO-HIDE FLASH MESSAGES
// ============================================================

function hideFlashMessages() {
    const messages =
        document.querySelectorAll(".flash-message");

    messages.forEach(function (message) {

        setTimeout(function () {

            message.style.opacity = "0";

            setTimeout(function () {
                message.remove();
            }, 500);

        }, 5000);

    });
}


// ============================================================
// MOBILE MENU CLOSE WHEN LINK IS CLICKED
// ============================================================

function closeMobileMenu() {
    const nav = document.querySelector(".nav-links");

    if (nav) {
        nav.classList.remove("show");
    }
}


// ============================================================
// PAGE LOAD
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        console.log(
            "Digital Lost & Found System Loaded"
        );

        hideFlashMessages();

        // Close mobile menu after clicking a link
        const navLinks =
            document.querySelectorAll(
                ".nav-links a"
            );

        navLinks.forEach(function (link) {

            link.addEventListener(
                "click",
                closeMobileMenu
            );

        });

    }
);