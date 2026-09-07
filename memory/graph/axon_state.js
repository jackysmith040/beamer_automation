/**
 * Axon State Master v7.0
 * The centralized state machine for the NeuroWiki Visualizer.
 * Decouples the UI controls from the D3/ForceGraph rendering logic.
 */

window.AxonState = {
    // Current Brain Data
    data: window.BRAIN_DATA || { nodes: [], links: [] },

    // View Settings
    is3D: true,
    theme: 'galaxy',
    orbitEnabled: false,
    focusNode: null,

    // Physics Parameters (Default/Calibrated)
    physics: {
        repulsion: -300,
        tension: 100,
        gravity: 0.1
    },

    // Theme Definitions
    themes: {
        galaxy: { bg: '#000000', link: 'rgba(255,255,255,0.1)', callosum: 'rgba(255,255,255,0.8)', left: '#00e5ff', right: '#ff00ff', wiki: '#ffff00', text: '#ffffff' },
        cyber: { bg: '#050510', link: 'rgba(0,255,100,0.1)', callosum: 'rgba(0,255,100,0.8)', left: '#00ff66', right: '#ff0033', wiki: '#00ccff', text: '#00ff66' },
        mono: { bg: '#0a0a0a', link: 'rgba(255,255,255,0.05)', callosum: 'rgba(255,255,255,0.5)', left: '#ffffff', right: '#888888', wiki: '#ffffff', text: '#c5c6c7' }
    },

    // Listeners and Dispatch
    listeners: [],
    
    subscribe(callback) {
        this.listeners.push(callback);
    },

    dispatch(action, payload) {
        console.log(`[AXON STATE] Dispatching: ${action}`, payload);
        
        switch(action) {
            case 'SET_MODE':
                this.is3D = payload;
                break;
            case 'SET_THEME':
                this.theme = payload;
                break;
            case 'SET_PHYSICS':
                this.physics = { ...this.physics, ...payload };
                break;
            case 'TOGGLE_ORBIT':
                this.orbitEnabled = !this.orbitEnabled;
                break;
            case 'SET_FOCUS':
                this.focusNode = payload;
                break;
        }

        // Notify all subscribers (UI and Graph)
        this.listeners.forEach(cb => cb(this));
    }
};
