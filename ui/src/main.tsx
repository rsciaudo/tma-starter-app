import { createRoot } from 'react-dom/client';
import { MantineProvider } from '@mantine/core';
import '@mantine/core/styles.css';
import './globals.css';
import App from './App';
import { theme } from './theme';

function main() {
    const rootEl = document.getElementById('app');
    if (!rootEl) {
        throw new Error('Root element not found');
    }
    const root = createRoot(rootEl);
    root.render(
        <MantineProvider theme={theme}>
            <App />
        </MantineProvider>
    );
}

main();
