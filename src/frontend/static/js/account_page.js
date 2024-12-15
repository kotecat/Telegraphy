pagesConfig = {
    limit: 10
}

pagesState = {
    color: 0,
    colorCount: 3,
    currentOffset: 0,
    alreadyLoaded: [],
    lastCount: 0,
    loadBtn: document.getElementById("load-next")
}


function handlePage(page) {
    const path = page.path.toLowerCase();
    const created = formatDateTime(page.created);
    const title = page.title;
    const views = page.views;

    if (pagesState.alreadyLoaded.includes(path)) {
        return;
    }
    pagesState.alreadyLoaded.push(path);
    pagesState.color++;
    if (pagesState.color >= pagesState.colorCount) {
        pagesState.color = 0;
    }

    // process
    const pageCardEl = document.createElement("div");
    pageCardEl.setAttribute("class", "card_page");
    pageCardEl.setAttribute("color_code", `${pagesState.color}`);

    const pageCardTDEl = document.createElement("div");
    pageCardTDEl.setAttribute("class", "card_page_td");

    const pageCardBVEl = document.createElement("div");
    pageCardBVEl.setAttribute("class", "card_page_bv");

    const pageButtonsEl = document.createElement("div");
    pageButtonsEl.setAttribute("class", "buttons");

    // add left side
    const titlePageEl = document.createElement("h4");
    titlePageEl.innerText = title;

    const datePageEl = document.createElement("p");
    datePageEl.innerText = created;
    datePageEl.style.color = "gray";

    pageCardTDEl.appendChild(titlePageEl);
    pageCardTDEl.appendChild(datePageEl);

    // add right side
    const pageAEl = document.createElement("a");
    pageAEl.setAttribute("href", `/${path}`);
    const pageButtonLinkEl = document.createElement("button");
    pageButtonLinkEl.innerText = "Go Page";

    const viewsPageEl = document.createElement("p");
    viewsPageEl.innerText = `views: ${views}`;
    viewsPageEl.style.color = "gray";

    pageButtonsEl.appendChild(pageButtonLinkEl);
    pageAEl.appendChild(pageButtonsEl);
    pageCardBVEl.appendChild(pageAEl);
    pageCardBVEl.appendChild(viewsPageEl);

    pageCardEl.appendChild(pageCardTDEl);
    pageCardEl.appendChild(pageCardBVEl);

    document.getElementById("cards_page").appendChild(pageCardEl);
}


function loadPages() {
    if (pagesState.loadBtn.disabled) {
        return;
    }
    pagesState.loadBtn.disabled = true;

    (async () => {
        const account = await autoCreateAccount();;

        const pages = await getPages(
            account.access_token,
            pagesConfig.limit, pagesState.currentOffset
        );
        const countPages = pages.length;

        if (pages === null) {
            alert("Error (see logs)");
            pagesState.loadBtn.disabled = false;
            return;
        }
        
        pagesState.currentOffset += countPages;
        pagesState.lastCount = countPages;

        pages.forEach((page) => {
            handlePage(page);
        });
        pagesState.loadBtn.disabled = false;
    })();

}

pagesState.loadBtn.addEventListener('click', () => {
    loadPages();
});


function checkScrollPosition() {
    const pageHeight = document.documentElement.scrollHeight;
    const scrollTop = window.scrollY || document.documentElement.scrollTop;
    const viewportHeight = window.innerHeight;

    if (scrollTop + viewportHeight >= pageHeight - 100) {
        if (pagesState.lastCount > 0) {
            console.log("Data load");
            loadPages();
        }   
    }
}


window.addEventListener('scroll', checkScrollPosition);

(async () => {
    await autoCreateAccount();
    pagesState.loadBtn.disabled = false;
    loadPages();
})();
