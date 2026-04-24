function svg(paths) {
    return '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">' + paths + "</svg>";
}

const ICONS = {
    dashboard: svg('<path d="M4 5h7v6H4zM13 5h7v10h-7zM4 13h7v6H4zM13 17h7v2h-7z"></path>'),
    users: svg('<path d="M16 19v-1a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v1"></path><circle cx="9.5" cy="7" r="3"></circle><path d="M21 19v-1a4 4 0 0 0-3-3.87"></path><path d="M16 4.13a3 3 0 0 1 0 5.75"></path>'),
    book: svg('<path d="M4 6.5A2.5 2.5 0 0 1 6.5 4H20v15H6.5A2.5 2.5 0 0 0 4 21V6.5z"></path><path d="M8 7h8"></path><path d="M8 11h8"></path>'),
    calendar: svg('<rect x="3" y="5" width="18" height="16" rx="2"></rect><path d="M16 3v4M8 3v4M3 10h18"></path>'),
    wallet: svg('<path d="M3 7a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v1H5a2 2 0 0 0-2 2z"></path><path d="M21 10v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path><circle cx="16.5" cy="14" r="1"></circle>'),
    award: svg('<circle cx="12" cy="8" r="4"></circle><path d="M8.5 13.5L7 21l5-2 5 2-1.5-7.5"></path>'),
    video: svg('<rect x="3" y="6" width="13" height="12" rx="2"></rect><path d="M16 10l5-3v10l-5-3z"></path>'),
    message: svg('<path d="M21 12a8.5 8.5 0 0 1-8.5 8.5H6l-3 3v-6.5A8.5 8.5 0 1 1 21 12z"></path>'),
    bot: svg('<rect x="5" y="8" width="14" height="10" rx="3"></rect><path d="M12 4v4M9 13h.01M15 13h.01M9 16h6"></path>'),
    bell: svg('<path d="M15 18H9"></path><path d="M18 16V11a6 6 0 1 0-12 0v5l-2 2h16z"></path>'),
    search: svg('<circle cx="11" cy="11" r="6"></circle><path d="M20 20l-3.5-3.5"></path>'),
    plus: svg('<path d="M12 5v14M5 12h14"></path>'),
    filter: svg('<path d="M4 6h16M7 12h10M10 18h4"></path>'),
    chevron: svg('<path d="M9 6l6 6-6 6"></path>'),
    menu: svg('<path d="M4 7h16M4 12h16M4 17h16"></path>'),
    logout: svg('<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><path d="M16 17l5-5-5-5"></path><path d="M21 12H9"></path>'),
    edit: svg('<path d="M12 20h9"></path><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"></path>'),
    close: svg('<path d="M6 6l12 12M18 6l-12 12"></path>'),
    home: svg('<path d="M3 11.5L12 4l9 7.5"></path><path d="M5 10.5V20h14v-9.5"></path>'),
    spark: svg('<path d="M12 3l1.8 4.8L19 9.6l-4.8 1.8L12 16l-2.2-4.6L5 9.6l5.2-1.8z"></path><path d="M19 3l.8 2.2L22 6l-2.2.8L19 9l-.8-2.2L16 6l2.2-.8z"></path>'),
    chart: svg('<path d="M5 19V9M12 19V5M19 19v-7"></path><path d="M3 19h18"></path>'),
    eye: svg('<path d="M2 12s4-6 10-6 10 6 10 6-4 6-10 6-10-6-10-6z"></path><circle cx="12" cy="12" r="3"></circle>')
};

export function icon(name) {
    return ICONS[name] || ICONS.dashboard;
}
