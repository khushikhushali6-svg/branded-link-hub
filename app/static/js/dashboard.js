async function loadLinks(){

    const token = localStorage.getItem("access_token");

    const response = await fetch(
        "/api/links",
        {
            headers:{
                "Authorization":
                "Bearer " + token
            }
        }
    );

    const data = await response.json();

    const container =
    document.getElementById("links");


    if(data.links){

        container.innerHTML = "";

        data.links.forEach(link => {

            container.innerHTML += `
                <div>
                    <h4>${link.title || "Untitled"}</h4>
                    <p>${link.original_url}</p>
                    <p>
                    Short URL:
                    ${link.short_url || link.slug}
                    </p>
                </div>
                <hr>
            `;

        });

    }
    else{
        container.innerHTML =
        "No links found.";
    }

}


loadLinks();

document
.getElementById("createLinkForm")
.addEventListener(
"submit",
async function(e){

    e.preventDefault();


    const response = await fetch(
        "/api/links",
        {
            method:"POST",
            headers:{
                "Content-Type":"application/json",
                "Authorization":
                "Bearer " + localStorage.getItem("access_token")
            },
            body:JSON.stringify({

                title:
                document.getElementById("title").value,

                original_url:
                document.getElementById("original_url").value,

                custom_slug:
                document.getElementById("custom_slug").value || null

            })
        }
    );


    const data = await response.json();


    document.getElementById("createMessage")
    .innerText =
    data.message || data.error;


    if(response.ok){

        loadLinks();

    }

});