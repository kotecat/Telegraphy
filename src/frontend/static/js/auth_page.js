document.getElementById('auth-token').addEventListener('click', () => {
    const authBtn = document.getElementById('auth-token');
    authBtn.disabled = true;

    const token = document.getElementById("input-token").value;
    if (!token || token.length < 10) {
        authBtn.disabled = false;
        alert("Bad Token");
        return;
    }

    (async () => {
        const account = await getAccount(token);
        authBtn.disabled = false;

        if (account) {
            setLocalToken(token);
            alert("Auth Successfully!");
        } else {
            alert("Error (see logs)");
        }
    })();
});


document.getElementById('copy-token').addEventListener('click', () => {
    const token = getLocalToken();

    if (!token) {
        return;
    }

    copyToClipboard(token);
});
