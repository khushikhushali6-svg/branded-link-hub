function getCsrfToken() {
    const cookie = document.cookie
        .split("; ")
        .find(row => row.startsWith("csrf_access_token="));

    return cookie ? cookie.split("=")[1] : "";
}



async function loadLinks(search = "", page = 1) {

    const response = await fetch(
        "/api/links?search=" +
        encodeURIComponent(search) +
        "&page=" +
        page,
        {
            headers: {
                "Authorization":
                    "Bearer " +
                    localStorage.getItem(
                        "access_token"
                    )
            }
        }
    );

    const data = await response.json();

    const container =
        document.getElementById("links");

    if (response.ok && data.links) {

        if (data.links.length === 0) {

            container.innerHTML =
                "<p>No links found.</p>";

        } else {

            let table = `
                <table
                    border="1"
                    cellpadding="10"
                    cellspacing="0"
                    width="100%"
                >

                    <thead>
                        <tr>
                            <th>Title</th>
                            <th>Original URL</th>
                            <th>Short URL</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>

                    <tbody>
            `;

            data.links.forEach(link => {

                table += `
                    <tr>

                        <td>
                            ${link.title || "Untitled"}
                        </td>

                        <td>
                            <a
                                href="${link.original_url}"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                ${link.original_url}
                            </a>
                        </td>

                        <td>
                            <a
                                href="/r/${link.slug}"
                                target="_blank"
                            >
                                /r/${link.slug}
                            </a>
                        </td>

                        <td>
                            ${
                                link.is_active
                                ? "Active"
                                : "Inactive"
                            }
                        </td>

                        <td>

                            <button
                                onclick="copyLink('${link.slug}')"
                            >
                                Copy
                            </button>

                            <button
                                onclick="deleteLink(${link.id})"
                            >
                                Delete
                            </button>

                            <button
                                onclick="viewAnalytics(${link.id})"
                            >
                                Analytics
                            </button>

                            <a
                                href="/api/links/${link.id}/qr"
                                target="_blank"
                            >
                                <button>
                                    QR Code
                                </button>
                            </a>

                        </td>

                    </tr>
                `;
            });

            table += `
                    </tbody>
                </table>
            `;

            container.innerHTML = table;
        }

        const pagination =
            data.pagination;

        document
        .getElementById("pageInfo")
        .innerText =
            "Page " +
            pagination.page +
            " of " +
            (pagination.pages || 1);

        document
        .getElementById("previousPage")
        .disabled =
            !pagination.has_prev;

        document
        .getElementById("nextPage")
        .disabled =
            !pagination.has_next;

    } else {

        container.innerHTML =
            data.error ||
            "No links found.";
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
                localStorage.getItem("access_token"),

                "X-CSRF-TOKEN": getCsrfToken()
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


    const confirmed = confirm(
        "Are you sure you want to delete this link?"
    );

    if (!confirmed) {
        return;
    }

    const response = await fetch(

        `/api/links/${id}`,

        {

            method:"DELETE",


            headers:{

                "Authorization":
                "Bearer " +
                localStorage.getItem("access_token"),

                "X-CSRF-TOKEN":getCsrfToken()

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


    const devices =
        analytics.devices;

    const maxDeviceClicks =
        Math.max(
            devices.Desktop,
            devices.Mobile,
            devices.Tablet,
            1
        );

    document.getElementById("devices").innerHTML = `
        <div class="analytics-chart">

            <div class="analytics-row">
                <div class="analytics-label">
                    Desktop
                </div>

                <div class="analytics-bar-container">
                    <div
                        class="analytics-bar"
                        style="width:${(devices.Desktop / maxDeviceClicks) * 100}%"
                    ></div>
                </div>

                <div class="analytics-value">
                    ${devices.Desktop} clicks
                </div>
            </div>


            <div class="analytics-row">
                <div class="analytics-label">
                    Mobile
                </div>

                <div class="analytics-bar-container">
                    <div
                        class="analytics-bar"
                        style="width:${(devices.Mobile / maxDeviceClicks) * 100}%"
                    ></div>
                </div>

                <div class="analytics-value">
                    ${devices.Mobile} clicks
                </div>
            </div>


            <div class="analytics-row">
                <div class="analytics-label">
                    Tablet
                </div>

                <div class="analytics-bar-container">
                    <div
                        class="analytics-bar"
                        style="width:${(devices.Tablet / maxDeviceClicks) * 100}%"
                    ></div>
                </div>

                <div class="analytics-value">
                    ${devices.Tablet} clicks
                </div>
            </div>

        </div>
    `;


    const referrers =
        analytics.referrers;

    const maxReferrerClicks =
        Math.max(
            ...referrers.map(
                item => item.clicks
            ),
            1
        );

    document.getElementById("referrers").innerHTML = "";

    referrers.forEach(
        function(item){

            const width =
                (item.clicks /
                maxReferrerClicks) * 100;

            document.getElementById(
                "referrers"
            ).innerHTML += `

                <div class="analytics-row">

                    <div class="analytics-label">
                        ${item.referrer}
                    </div>

                    <div class="analytics-bar-container">
                        <div
                            class="analytics-bar"
                            style="width:${width}%"
                        ></div>
                    </div>

                    <div class="analytics-value">
                        ${item.clicks} clicks
                    </div>

                </div>
            `;
        }
    );


    const clicksOverTime =
        analytics.clicks_over_time;

    const maxDailyClicks =
        Math.max(
            ...clicksOverTime.map(
                item => item.clicks
            ),
            1
        );

    document.getElementById(
        "clicksOverTime"
    ).innerHTML = "";

    clicksOverTime.forEach(
        function(item){

            const width =
                (item.clicks /
                maxDailyClicks) * 100;

            document.getElementById(
                "clicksOverTime"
            ).innerHTML += `

                <div class="analytics-row">

                    <div class="analytics-label">
                        ${item.date}
                    </div>

                    <div class="analytics-bar-container">
                        <div
                            class="analytics-bar"
                            style="width:${width}%"
                        ></div>
                    </div>

                    <div class="analytics-value">
                        ${item.clicks} clicks
                    </div>

                </div>
            `;
        }
    );
}

document
.getElementById("saveTheme")
.addEventListener(
    "click",
    async function(){

        const theme =
            document
            .getElementById("theme")
            .value;

        const profileResponse =
            await fetch(
                "/api/profile",
                {
                    headers:{
                        "Authorization":
                        "Bearer " +
                        localStorage.getItem("access_token")
                    }
                }
            );

        const profileData =
            await profileResponse.json();

        if(!profileResponse.ok){
            document
            .getElementById("themeMessage")
            .innerText =
                profileData.error ||
                "Unable to load profile.";

            return;
        }

        const profile =
            profileData.profile;

        const response =
            await fetch(
                "/api/profile",
                {
                    method:"POST",
                    headers:{
                        "Content-Type":
                        "application/json",

                        "X-CSRF-TOKEN":
                        getCsrfToken()
                },
                    body:JSON.stringify({
                        display_name:
                            profile.display_name,
                        bio:
                            profile.bio,
                        avatar_url:
                            profile.avatar_url,
                        theme:
                            theme
                    })
                }
            );

        const data =
            await response.json();

        document
        .getElementById("themeMessage")
        .innerText =
            data.message ||
            data.error;
    }
);

async function loadProfile() {

    const response = await fetch(
        "/api/profile",
        {
            headers: {
                "Authorization":
                    "Bearer " +
                    localStorage.getItem("access_token")
            }
        }
    );

    const data = await response.json();

    if (!response.ok) {
        document.getElementById("profileMessage").innerText =
            data.error || "Unable to load profile.";

        return;
    }

    const profile = data.profile;

    document.getElementById("displayName").value =
        profile.display_name || "";

    document.getElementById("bio").value =
        profile.bio || "";

    document.getElementById("theme").value =
        profile.theme || "minimal-light";
}


document
.getElementById("saveProfile")
.addEventListener(
    "click",
    async function () {

        const displayName =
            document
            .getElementById("displayName")
            .value
            .trim();

        const bio =
            document
            .getElementById("bio")
            .value
            .trim();

        const profileResponse =
            await fetch(
                "/api/profile",
                {
                    headers: {
                        "Authorization":
                            "Bearer " +
                            localStorage.getItem("access_token"),
                        "X-CSRF-TOKEN":
                            getCsrfToken()
                    }
                }
            );

        const profileData =
            await profileResponse.json();

        if (!profileResponse.ok) {
            document
            .getElementById("profileMessage")
            .innerText =
                profileData.error ||
                "Unable to load profile.";

            return;
        }

        const profile =
            profileData.profile;

        const response =
            await fetch(
                "/api/profile",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json",

                        "Authorization":
                            "Bearer " +
                            localStorage.getItem("access_token")
                    },

                    body: JSON.stringify({
                        display_name:
                            displayName,

                        bio:
                            bio,

                        avatar_url:
                            profile.avatar_url,

                        theme:
                            profile.theme
                    })
                }
            );

        const data =
            await response.json();

        document
        .getElementById("profileMessage")
        .innerText =
            data.message ||
            data.error;
    }
);


loadProfile();

document
.getElementById("uploadAvatar")
.addEventListener(
    "click",
    async function () {

        const fileInput =
            document.getElementById("avatar");

        if (!fileInput.files.length) {
            document
            .getElementById("avatarMessage")
            .innerText =
                "Please select an image.";

            return;
        }

        const formData =
            new FormData();

        formData.append(
            "avatar",
            fileInput.files[0]
        );

        const response =
            await fetch(
                "/api/profile/avatar",
                {
                    method: "POST",

                    headers: {
                        "X-CSRF-TOKEN":
                        getCsrfToken()
                    },

                    body: formData
                }
            );

        const data =
            await response.json();

        document
        .getElementById("avatarMessage")
        .innerText =
            data.message ||
            data.error;

        if (response.ok) {
            fileInput.value = "";
        }
    }
);


async function loadSocialLinks() {

    const response = await fetch(
        "/api/social",
        {
            headers: {
                "Authorization":
                    "Bearer " +
                    localStorage.getItem("access_token")
            }
        }
    );

    const data = await response.json();

    const container =
        document.getElementById("socialLinks");

    if (!response.ok) {
        container.innerText =
            data.error ||
            "Unable to load social links.";

        return;
    }

    if (!data.social_links.length) {
        container.innerText =
            "No social links added.";

        return;
    }

    container.innerHTML = "";

    data.social_links.forEach(
        function (social) {

            const item =
                document.createElement("div");

            item.innerHTML = `
                <input
                    type="text"
                    id="platform-${social.id}"
                    value="${social.platform}"
                >

                <br><br>

                <input
                    type="url"
                    id="url-${social.id}"
                    value="${social.url}"
                >

                <br><br>

                <label>
                    <input
                        type="checkbox"
                        id="visible-${social.id}"
                        ${social.is_visible ? "checked" : ""}
                    >
                    Visible
                </label>

                <br><br>

                <button
                    type="button"
                    onclick="updateSocialLink(${social.id})"
                >
                    Save Changes
                </button>

                <button
                    type="button"
                    onclick="deleteSocialLink(${social.id})"
                >
                    Delete
                </button>

                <hr>
            `;

            container.appendChild(item);
        }
    );
}

async function updateSocialLink(id) {

    const platform =
        document
        .getElementById("platform-" + id)
        .value
        .trim();

    const url =
        document
        .getElementById("url-" + id)
        .value
        .trim();

    const isVisible =
        document
        .getElementById("visible-" + id)
        .checked;

    if (!platform || !url) {

        document
        .getElementById("socialMessage")
        .innerText =
            "Platform and URL are required.";

        return;
    }

    const response =
        await fetch(
            "/api/social/" + id,
            {
                method: "PATCH",

                headers: {
                    "Content-Type":
                        "application/json",

                    "X-CSRF-TOKEN":
                        getCsrfToken()
                },

                body: JSON.stringify({
                    platform: platform,
                    url: url,
                    is_visible: isVisible
                })
            }
        );

    const data =
        await response.json();

    document
    .getElementById("socialMessage")
    .innerText =
        data.message ||
        data.error;

    if (response.ok && data.social_link) {
        document
        .getElementById("socialMessage")
        .innerText =
            data.message +
            " Saved as: " +
            data.social_link.platform;
    }

    if (response.ok) {
        loadSocialLinks();
    }
}


document
.getElementById("addSocialLink")
.addEventListener(
    "click",
    async function () {

        const platform =
            document
            .getElementById("socialPlatform")
            .value
            .trim();

        const url =
            document
            .getElementById("socialUrl")
            .value
            .trim();

        if (!platform || !url) {
            document
            .getElementById("socialMessage")
            .innerText =
                "Platform and URL are required.";

            return;
        }

        const response =
            await fetch(
                "/api/social",
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRF-TOKEN": getCsrfToken()
                    },
                    body: JSON.stringify({
                        platform: platform,
                        url: url
                    })
                }
            );

        const data =
            await response.json();

        document
        .getElementById("socialMessage")
        .innerText =
            data.message ||
            data.error;

        if (response.ok) {

            document
            .getElementById("socialPlatform")
            .value = "";

            document
            .getElementById("socialUrl")
            .value = "";

            loadSocialLinks();
        }
    }
);


async function deleteSocialLink(id) {

    const confirmed = confirm(
        "Are you sure you want to delete this social link?"
    );

    if (!confirmed) {
        return;
    }    
    const response =
        await fetch(
            "/api/social/" + id,
            {
                method: "DELETE",

                headers: {
                    "X-CSRF-TOKEN":
                        getCsrfToken()
                }
            }
        );

    const data =
        await response.json();

    document
    .getElementById("socialMessage")
    .innerText =
        data.message ||
        data.error;

    if (response.ok) {
        loadSocialLinks();
    }
}


loadSocialLinks();

document
.getElementById("logout")
.addEventListener(
    "click",
    async function () {

        await fetch(
            "/api/auth/logout",
            {
                method: "POST"
            }
        );

        localStorage.removeItem(
            "access_token"
        );

        window.location.href =
            "/login";
    }
);