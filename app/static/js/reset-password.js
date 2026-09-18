const token = window.location.pathname.split("/").pop();


document
.getElementById("resetForm")
.addEventListener(
"submit",
async function(e){

    e.preventDefault();


    const response = await fetch(
        `/api/auth/reset-password/${token}`,
        {
            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({

                password:
                document
                .getElementById("password")
                .value

            })
        }
    );


    const data = await response.json();


    document
    .getElementById("message")
    .innerText =
    data.message || data.error;


});