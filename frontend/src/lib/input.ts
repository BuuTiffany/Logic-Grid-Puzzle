export function sanitizeInput(
    value: string,
    options: {
        maxLength?: number;
        trim?: boolean;
        collapseWhitespace?: boolean;
        allowed?: RegExp;
        lowercase?: boolean;
    } = {}
): string {
    const {
        maxLength = 120,
        trim = true,
        collapseWhitespace = false,
        allowed,
        lowercase = false,
    } = options;

    let clean = String(value ?? '').replace(/[\x00-\x1F\x7F]/g, '');
    if (allowed) clean = [...clean].filter((ch) => allowed.test(ch)).join('');
    if (collapseWhitespace) clean = clean.replace(/\s+/g, ' ');
    if (trim) clean = clean.trim();
    if (lowercase) clean = clean.toLowerCase();
    return clean.slice(0, maxLength);
}

export function sanitizeUsernameInput(value: string): string {
    return sanitizeInput(value, {
        maxLength: 30,
        collapseWhitespace: true,
        allowed: /[A-Za-z0-9_ .-]/,
    });
}

export function sanitizeEmailInput(value: string): string {
    return sanitizeInput(value, {
        maxLength: 254,
        lowercase: true,
    });
}

export function sanitizePasswordInput(value: string): string {
    return sanitizeInput(value, {
        maxLength: 128,
        trim: false,
    });
}
