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
    console.log("LOGIN RESPONSE:", data);


    if(response.ok){ 

        console.log("LOGIN RESPONSE:", data);
        window.location.href = "/dashboard";

    }
    else{

        document.getElementById("message")
        .innerText =
        data.error;

    }

});
