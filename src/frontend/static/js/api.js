var currAccount;
var currPage;

const copyToClipboard = str => {
    const el = document.createElement('textarea');
    el.value = str;
    el.setAttribute('readonly', '');
    el.style.position = 'absolute';
    el.style.left = '-9999px';
    document.body.appendChild(el);
    const selected =
        document.getSelection().rangeCount > 0
        ? document.getSelection().getRangeAt(0)
        : false;
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);
    if (selected) {
        document.getSelection().removeAllRanges();
        document.getSelection().addRange(selected);
    }
};


const formatDateTime = (utcDateString) => {
    const utcDate = new Date(`${utcDateString}Z`);
    const userTimeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;

    const formattedDate = utcDate.toLocaleString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
    });

    return formattedDate.replace("at", "•");
}

function getLocalToken() {
    return localStorage.getItem('token_');
}

function setLocalToken(token_) {
    localStorage.setItem("token_", token_);
}

async function sendRequestGet(uri) {
    const url = `${window.location.origin}${uri}`;
    try {
        const response = await fetch(url, { method: 'GET' });
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const result = await response.json();
        console.log('Success:', result);
        return result;

    } catch (error) {
        console.error('Error:', error);
        return null;
    }
}

async function sendRequestPost(uri, data) {
    const url = `${window.location.origin}${uri}`;

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: data,
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const result = await response.json();
        console.log('Success:', result);
        return result;

    } catch (error) {
        console.error('Error:', error);
        return null;
    }
}

async function getAccount(token) {
    return sendRequestGet(`/api/getAccountInfo?token=${token}`);
}

async function createAccount() {
    return sendRequestGet(`/api/createAccount?short_name=Anonymous`);
}

async function getPageWithToken(pageUri, token) {
    if (token) {
        return sendRequestGet(`/api/getPage/${pageUri}?token=${token}&return_content=false`);
    }
    return sendRequestGet(`/api/getPage/${pageUri}?return_content=false`);
}

async function editPage(token, pageUri, data) {
    return sendRequestPost(`/api/editPage/${pageUri}`, `token=${token}&${data}`);
}

async function createPage(token, data) {
    return sendRequestPost(`/api/createPage`, `token=${token}&${data}`);
}

async function deletePage(token, pageUri) {
    return sendRequestGet(`/api/deletePage/${pageUri}?token=${token}`);
}

async function addView(pageUri) {
    return sendRequestGet(`/api/addView/${pageUri}`);
}

async function getPages(token, limit, offset) {
    return sendRequestGet(`/api/getPages?token=${token}&limit=${limit}&offset=${offset}`);
}

async function editProfileInfo(token, authorName, authorUrl) {
    return sendRequestGet(`/api/editAccountInfo?token=${token}&author_name=${authorName}&author_url=${authorUrl}`);
}

async function autoCreateAccount() {
    if (currAccount) {
        return currAccount;
    }

    let token_ = getLocalToken()
    let account;

    if (token_) {
        account = await getAccount(token_);
        if (account) {
            currAccount = account;
            return account;
        }
    }

    account = await createAccount();
    currAccount = account;
    setLocalToken(account.access_token)

    return account;
}

async function getPageInfo() {
    if (window.location.pathname == "/") {
        return null;
    }
    if (currPage) {
        return currPage;
    }
    let account = await autoCreateAccount();
    let page;

    if (account) {
        page = await getPageWithToken(window.location.pathname.replace("/", ""), account.access_token);
    } else {
        page = await getPageWithToken(window.location.pathname.replace("/", ""), account.access_token);
    }
    
    currPage = page;
    return page;
}

async function isAllowEdit() {
    if (window.location.pathname == "/") {
        return false;
    }

    let page = await getPageInfo();
    if (page && page.can_edit === true) {
        return true;
    }
    return false;
}
