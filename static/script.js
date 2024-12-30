let typingTimer;

function showMessage(text, type) {
    console.log(`Showing message: ${text} (${type})`);
    const messageElement = document.getElementById('message');
    messageElement.textContent = text;
    messageElement.className = `message ${type} visible`;
    setTimeout(() => {
        messageElement.className = `message ${type}`;
        console.log('Message hidden');
    }, 2000);
}

function copyToClipboard(text) {
    console.log('Attempting to copy to clipboard');
    const textBlob = new Blob([text], { type: 'text/plain' });
    const clipboardItem = new ClipboardItem({ 'text/plain': textBlob });
    
    navigator.clipboard.write([clipboardItem]).then(() => {
        console.log('Copy successful');
        showMessage('Copied', 'success');
    }).catch((error) => {
        const tempInput = document.createElement('textarea');
        tempInput.value = text;
        document.body.appendChild(tempInput);
        tempInput.select();
        document.execCommand('copy');
        document.body.removeChild(tempInput);
        
        console.log('Copy successful (fallback)');
        showMessage('Copied', 'success');
    });
}

function generatePassword() {
    const specification = document.getElementById('specification').value;
    
    if (!specification.trim()) {
        console.log('Empty specification, skipping password generation');
        return;
    }
    
    document.getElementById('loading-spinner').classList.add('loading');
    
    console.log('Generating password with specification:', specification);
    fetch('/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `specification=${encodeURIComponent(specification)}`
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('loading-spinner').classList.remove('loading');
        
        if (data.success) {
            console.log('Password generated successfully');
            const passwordOutput = document.getElementById('password-output');
            passwordOutput.value = data.password;
            copyToClipboard(data.password);

            setTimeout(() => {
                passwordOutput.classList.add('password-fade');
                setTimeout(() => {
                    passwordOutput.value = '';
                    passwordOutput.classList.remove('password-fade');
                    console.log('Password cleared for security');
                }, 500);
            }, 5000);
        } else {
            console.error('Generation error:', data.error);
            showMessage(data.error, 'error');
        }
    })
    .catch((error) => {
        document.getElementById('loading-spinner').classList.remove('loading');
        console.error('Generation failed:', error);
        showMessage('Generation failed', 'error');
    });
}


document.getElementById('specification').addEventListener('keyup', function() {
    console.log('Keyup event - starting timer for password generation');
    clearTimeout(typingTimer);
    typingTimer = setTimeout(generatePassword, 2000);
});

document.getElementById('specification').addEventListener('keydown', function() {
    console.log('Keydown event - clearing timer');
    clearTimeout(typingTimer);
});

document.querySelector('.usage-toggle').addEventListener('click', function() {
    const content = document.querySelector('.usage-content');
    content.classList.toggle('expanded');
    this.textContent = content.classList.contains('expanded') ? 'How to use ▴' : 'How to use ▾';
});
