// document.addEventListener("DOMContentLoaded", () => {
//     document.getElementById("signForm").addEventListener("submit", async (e) => {
//         e.preventDefault();

//         const username = document.getElementById("username").value;
//         const email = document.getElementById("email").value;
//         const password = document.getElementById("password").value;

//         const formData = new FormData();
//         formData.append("username", username);
//         formData.append("email", email);
//         formData.append("password", password);

//         try {
//             const response = await fetch("/register", {
//                 method: "POST",
//                 body: formData
//             });

//             if (response.ok) {
//                 showToast();
//                 document.getElementById("signForm").reset();
//             } else {
//                 console.error("Registration failed:", response.status, response.statusText);
//             }
//         } catch (error) {
//             console.error('Error:', error);
//         }
//     });
// });

// function showToast() {
//     const toast = document.getElementById("toast");
//     toast.classList.add("show");
//     setTimeout(() => {
//         toast.classList.remove("show");
//     }, 3000);
// }

// const errormessage = document.getElementById("messagebox");
// setTimeout(() => {
//     errormessage.remove("show");
// }, 6000);

// const toast = document.getElementById("toast");
// setTimeout(() => {
//     toast.classList.remove("show");
// }, 6000);



// document.getElementById("profile-form").addEventListener("submit", async function(event) {
//     event.preventDefault();
    
//     const formData = new FormData(this);

//     const response = await fetch("/update_profile", {
//         method: "POST",
//         body: formData
//     });

//     if (response.ok) {
//         showToast("Profile updated successfully!")
//     } else {
//         showToast("Failed to update profile")
//     }
// });

// function showToast(message, isError = false) {
//     let toast = document.getElementById("toast");
//     toast.innerText = message;
//     toast.className = isError ? "toast error" : "toast";
//     toast.style.display = "block";
//     setTimeout(() => { toast.style.display = "none"; }, 3000);
// }



const updatemessage = document.getElementById("flash-messages");
setTimeout(() => {
    updatemessage.remove("show");
}, 3000);