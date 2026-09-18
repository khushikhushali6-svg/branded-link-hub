document
    .getElementById("forgotForm")
    .addEventListener(
        "submit",
        async function(e){

            e.preventDefault();


            const response = await fetch(
                "/api/auth/forgot-password",
                {
                    method:"POST",

                    headers:{
                        "Content-Type":"application/json"
                    },

                    body:JSON.stringify({

                        email:
                        document
                        .getElementById("email")
                        .value
                        .trim()

                    })
                }
            );


            const data = await response.json();


            document
            .getElementById("message")
            .innerText =
            data.message || data.error;


            if(response.ok && data.reset_url){

                document
                .getElementById("resetLink")
                .innerHTML = `

                    <p>
                    Reset Password Link:
                    </p>

                    <a href="${data.reset_url}">
                        Click Here
                    </a>

                `;
            }

        }
    );
    