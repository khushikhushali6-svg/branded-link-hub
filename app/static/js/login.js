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


    if(response.ok){ 

        console.log("TOKEN:", data.access_token);
        
        localStorage.setItem(
            "access_token",
            data.access_token
        );

        window.location.href = "/dashboard";

    }
    else{

        document.getElementById("message")
        .innerText =
        data.error;

    }

});
