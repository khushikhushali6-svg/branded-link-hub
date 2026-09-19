async function loadLinks(search = "", page = 1) {

    const response = await fetch(
        "/api/links?search=" + encodeURIComponent(search) + "&page=" + page,
        {
            headers:{
                "Authorization":
                "Bearer " + localStorage.getItem("access_token")
            }
        }
    );


    const data = await response.json();


    const container =
    document.getElementById("links");


    if(response.ok && data.links){

        container.innerHTML = "";


        data.links.forEach(link => {


            container.innerHTML += `

            <div>

                <h4>
                ${link.title || "Untitled"}
                </h4>


                <p>
                ${link.original_url}
                </p>


                <p>
                Short URL:

                <a href="/r/${link.slug}" target="_blank">
                /r/${link.slug}
                </a>
                </p>


                <p>
                Status:
                ${link.is_active ? "Active" : "Inactive"}
                </p>


                <button onclick="copyLink('${link.slug}')">
                    Copy
                </button>


                <button onclick="deleteLink(${link.id})">
                    Delete
                </button>

                <button onclick="viewAnalytics(${link.id})">
                    Analytics
                </button>

                <a href="/api/links/${link.id}/qr">
                    <button>
                        QR Code
                    </button>
                </a>


            </div>

            <hr>

            `;


        });

        const pagination = data.pagination;

        document.getElementById("pageInfo").innerText =
            "Page " + pagination.page + " of " + (pagination.pages || 1);

        document.getElementById("previousPage").disabled =
            !pagination.has_prev;

        document.getElementById("nextPage").disabled =
            !pagination.has_next;


    }
    else{

        container.innerHTML =
        data.error || "No links found.";

    }

}


loadLinks();

document
.getElementById("previousPage")
.addEventListener(
    "click",
    function(){
        const currentPage =
            Number(
                document
                .getElementById("pageInfo")
                .innerText
                .split(" ")[1]
            );

        const search =
            document
            .getElementById("search")
            .value
            .trim();

        loadLinks(
            search,
            currentPage - 1
        );
    }
);

document
.getElementById("nextPage")
.addEventListener(
    "click",
    function(){
        const currentPage =
            Number(
                document
                .getElementById("pageInfo")
                .innerText
                .split(" ")[1]
            );

        const search =
            document
            .getElementById("search")
            .value
            .trim();

        loadLinks(
            search,
            currentPage + 1
        );
    }
);


document
.getElementById("searchButton")
.addEventListener(
    "click",
    function(){
        loadLinks(
            document
            .getElementById("search")
            .value
            .trim()
        );
    }
);


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

                "Content-Type":
                "application/json",

                "Authorization":
                "Bearer " +
                localStorage.getItem("access_token")

            },


            body:JSON.stringify({

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



    const data =
    await response.json();



    document
    .getElementById("createMessage")
    .innerText =
    data.message || data.error;



    if(response.ok){

        document
        .getElementById("createLinkForm")
        .reset();


        loadLinks();

    }


});





async function copyLink(slug){


    const url =
    window.location.origin +
    "/r/" +
    slug;


    await navigator.clipboard.writeText(url);



    alert(
        "Short link copied!"
    );


}






async function deleteLink(id){


    const response = await fetch(

        `/api/links/${id}`,

        {

            method:"DELETE",


            headers:{

                "Authorization":
                "Bearer " +
                localStorage.getItem("access_token")

            }

        }

    );



    const data =
    await response.json();



    alert(
        data.message || data.error
    );



    if(response.ok){

        loadLinks();

    }

}

async function viewAnalytics(id){

    const response = await fetch(
        `/api/links/${id}/analytics`,
        {
            headers:{
                "Authorization":
                "Bearer " +
                localStorage.getItem("access_token")
            }
        }
    );

    const data = await response.json();

    if(!response.ok){
        alert(data.error || "Unable to load analytics.");
        return;
    }

    const analytics = data.analytics;

    document.getElementById("analytics").style.display = "block";

    document.getElementById("totalClicks").innerText =
        "Total Clicks: " +
        analytics.total_clicks;

    document.getElementById("uniqueVisitors").innerText =
        "Unique Visitors: " +
        analytics.unique_visitors;

    document.getElementById("devices").innerHTML = `
        <p>Desktop: ${analytics.devices.Desktop}</p>
        <p>Mobile: ${analytics.devices.Mobile}</p>
        <p>Tablet: ${analytics.devices.Tablet}</p>
    `;

    document.getElementById("referrers").innerHTML = "";

    analytics.referrers.forEach(item => {

        document.getElementById("referrers").innerHTML += `
            <p>
                ${item.referrer}: ${item.clicks} clicks
            </p>
        `;

    });

    document.getElementById("clicksOverTime").innerHTML = "";

    analytics.clicks_over_time.forEach(item => {

        document.getElementById("clicksOverTime").innerHTML += `
            <p>
                ${item.date}: ${item.clicks} clicks
            </p>
        `;

    });
}