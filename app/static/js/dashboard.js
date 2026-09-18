async function loadLinks() {

    const response = await fetch(
        "/api/links",
        {
            credentials: "include"
        }
    );

    const data = await response.json();

    const container =
        document.getElementById("links");

    if (response.ok && data.links) {

        container.innerHTML = "";

        data.links.forEach(link => {

            container.innerHTML += `
                <div>
                    <h4>${link.title || "Untitled"}</h4>

                    <p>${link.original_url}</p>

                    <p>
                        Short URL:
                        <a href="${link.short_url || "/" + link.slug}" target="_blank">
                            ${link.short_url || link.slug}
                        </a>
                    </p>

                    <p>
                        Status:
                        ${link.is_active ? "Active" : "Inactive"}
                    </p>
                </div>

                <hr>
            `;

        });

    }
    else {

        container.innerHTML =
            data.error || "No links found.";

    }

}


loadLinks();


document
    .getElementById("createLinkForm")
    .addEventListener(
        "submit",
        async function(e) {

            e.preventDefault();

            const response = await fetch(
                "/api/links",
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    credentials: "include",

                    body: JSON.stringify({

                        title:
                            document
                                .getElementById("title")
                                .value,

                        original_url:
                            document
                                .getElementById("original_url")
                                .value,

                        custom_slug:
                            document
                                .getElementById("custom_slug")
                                .value
                                .trim() || null

                    })
                }
            );


            const data = await response.json();


            document
                .getElementById("createMessage")
                .innerText =
                data.message || data.error;


            if (response.ok) {

                document
                    .getElementById("createLinkForm")
                    .reset();

                loadLinks();

            }

        }
    );