import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import {
    Card,
    CardHeader,
    CardTitle,
    CardDescription,
    CardContent,
    CardFooter
} from './card';

describe('Card', () => {
    describe('Card Component', () => {
        it('should render with default classes', () => {
            render(<Card data-testid="card">Content</Card>);
            const card = screen.getByTestId('card');

            expect(card).toBeInTheDocument();
            expect(card).toHaveAttribute('data-slot', 'card');
            expect(card).toHaveClass('bg-card');
        });

        it('should render children', () => {
            render(<Card>Card Content</Card>);
            expect(screen.getByText('Card Content')).toBeInTheDocument();
        });

        it('should apply custom className', () => {
            render(<Card className="custom-card" data-testid="card">Content</Card>);
            expect(screen.getByTestId('card')).toHaveClass('custom-card');
        });
    });

    describe('CardHeader Component', () => {
        it('should render with correct data-slot', () => {
            render(<CardHeader data-testid="header">Header</CardHeader>);
            expect(screen.getByTestId('header')).toHaveAttribute('data-slot', 'card-header');
        });
    });

    describe('CardTitle Component', () => {
        it('should render with correct styling', () => {
            render(<CardTitle>Title Text</CardTitle>);
            const title = screen.getByText('Title Text');

            expect(title).toHaveAttribute('data-slot', 'card-title');
            expect(title).toHaveClass('font-semibold');
        });
    });

    describe('CardDescription Component', () => {
        it('should render with muted styling', () => {
            render(<CardDescription>Description text</CardDescription>);
            const desc = screen.getByText('Description text');

            expect(desc).toHaveAttribute('data-slot', 'card-description');
            expect(desc).toHaveClass('text-muted-foreground');
        });
    });

    describe('CardContent Component', () => {
        it('should render children in content area', () => {
            render(<CardContent>Main content here</CardContent>);
            expect(screen.getByText('Main content here')).toHaveAttribute('data-slot', 'card-content');
        });
    });

    describe('CardFooter Component', () => {
        it('should render with flex layout', () => {
            render(<CardFooter data-testid="footer">Footer</CardFooter>);
            const footer = screen.getByTestId('footer');

            expect(footer).toHaveAttribute('data-slot', 'card-footer');
            expect(footer).toHaveClass('flex');
        });
    });

    describe('Composed Card', () => {
        it('should render a complete card structure', () => {
            render(
                <Card data-testid="full-card">
                    <CardHeader>
                        <CardTitle>Card Title</CardTitle>
                        <CardDescription>Card description text</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <p>This is the main content.</p>
                    </CardContent>
                    <CardFooter>
                        <button>Action</button>
                    </CardFooter>
                </Card>
            );

            expect(screen.getByText('Card Title')).toBeInTheDocument();
            expect(screen.getByText('Card description text')).toBeInTheDocument();
            expect(screen.getByText('This is the main content.')).toBeInTheDocument();
            expect(screen.getByRole('button', { name: 'Action' })).toBeInTheDocument();
        });
    });
});
