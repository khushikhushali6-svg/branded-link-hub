document
.getElementById("loginForm")
.addEventListener(
"submit",
async function(e){

    e.preventDefault();


    const response = await fetch(
        "/api/auth/login",
        {
            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({

                identifier:
                document.getElementById("identifier").value,

                password:
                document.getElementById("password").value

            })
        }
    );



    const data = await response.json();


    console.log(
        "LOGIN RESPONSE:",
        data
    );



    if(response.ok){


        localStorage.setItem(
            "access_token",
            data.access_token
        );


        console.log(
            "TOKEN SAVED:",
            localStorage.getItem("access_token")
        );


        window.location.href =
        "/dashboard";


    }
    else{


        document
        .getElementById("message")
        .innerText =
        data.error;


    }

});