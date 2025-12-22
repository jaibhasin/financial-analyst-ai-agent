// Loading skeleton components for better UX
import React from 'react';

export function AnalysisLoadingSkeleton() {
    return (
        <div className="container mt-3">
            {/* Header Skeleton */}
            <div className="flex justify-between items-center mb-3" style={{ gap: '1rem' }}>
                <div>
                    <div className="skeleton" style={{ width: '150px', height: '40px', marginBottom: '0.5rem' }} />
                    <div className="skeleton" style={{ width: '250px', height: '20px' }} />
                </div>
                <div>
                    <div className="skeleton" style={{ width: '200px', height: '60px' }} />
                </div>
            </div>

            {/* Tabs Skeleton */}
            <div className="flex gap-2 mb-3">
                <div className="skeleton" style={{ width: '100px', height: '40px' }} />
                <div className="skeleton" style={{ width: '120px', height: '40px' }} />
                <div className="skeleton" style={{ width: '100px', height: '40px' }} />
            </div>

            {/* Content Skeleton */}
            <div className="analysis-grid">
                {[1, 2, 3, 4].map((i) => (
                    <div key={i} className="card">
                        <div className="skeleton" style={{ width: '60%', height: '24px', marginBottom: '1rem' }} />
                        <div className="skeleton" style={{ width: '100%', height: '150px', marginBottom: '0.5rem' }} />
                        <div className="skeleton" style={{ width: '80%', height: '20px' }} />
                    </div>
                ))}
            </div>
        </div>
    );
}

export function QuoteLoadingSkeleton() {
    return (
        <div className="card" style={{ padding: '1.5rem' }}>
            <div className="skeleton" style={{ width: '120px', height: '24px', marginBottom: '1rem' }} />
            <div className="skeleton" style={{ width: '180px', height: '36px', marginBottom: '0.5rem' }} />
            <div className="skeleton" style={{ width: '100px', height: '20px' }} />
        </div>
    );
}
