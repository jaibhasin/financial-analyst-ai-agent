'use client';

import React, { Component, ReactNode } from 'react';
import { AlertTriangle } from 'lucide-react';

interface Props {
    children: ReactNode;
    fallback?: ReactNode;
}

interface State {
    hasError: boolean;
    error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = { hasError: false };
    }

    static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error };
    }

    componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
        console.error('Error caught by boundary:', error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            if (this.props.fallback) {
                return this.props.fallback;
            }

            return (
                <div className="container mt-4">
                    <div className="card text-center">
                        <AlertTriangle size={48} className="text-warning mb-2" style={{ margin: '0 auto' }} />
                        <h2>Something went wrong</h2>
                        <p className="text-muted mt-1">
                            {this.state.error?.message || 'An unexpected error occurred'}
                        </p>
                        <button
                            className="btn btn-primary mt-3"
                            onClick={() => this.setState({ hasError: false, error: undefined })}
                        >
                            Try Again
                        </button>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}
