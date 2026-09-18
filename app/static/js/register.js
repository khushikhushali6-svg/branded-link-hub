document
    .getElementById("registerForm")
    .addEventListener(
        "submit",
        async function(e) {

            e.preventDefault();

            const response = await fetch(
                "/api/auth/register",
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({

                        username:
                            document
                                .getElementById("username")
                                .value
                                .trim(),

                        email:
                            document
                                .getElementById("email")
                                .value
                                .trim(),

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

            if (response.ok && data.verification_url) {

                document
                    .getElementById("verification")
                    .innerHTML = `
                        <p>
                            Email verification simulation:
                        </p>

                        <a href="${data.verification_url}">
                            Verify Email
                        </a>
                    `;
            }
        }
    );