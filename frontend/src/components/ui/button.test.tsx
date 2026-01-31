import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Button } from './button';

describe('Button', () => {
    describe('Rendering', () => {
        it('should render with default props', () => {
            render(<Button>Click me</Button>);

            const button = screen.getByRole('button', { name: /click me/i });
            expect(button).toBeInTheDocument();
            expect(button).toHaveAttribute('data-variant', 'default');
            expect(button).toHaveAttribute('data-size', 'default');
        });

        it('should render children correctly', () => {
            render(<Button>Test Label</Button>);
            expect(screen.getByText('Test Label')).toBeInTheDocument();
        });

        it('should apply custom className', () => {
            render(<Button className="custom-class">Button</Button>);
            const button = screen.getByRole('button');
            expect(button).toHaveClass('custom-class');
        });
    });

    describe('Variants', () => {
        it('should render destructive variant', () => {
            render(<Button variant="destructive">Delete</Button>);
            expect(screen.getByRole('button')).toHaveAttribute('data-variant', 'destructive');
        });

        it('should render outline variant', () => {
            render(<Button variant="outline">Outline</Button>);
            expect(screen.getByRole('button')).toHaveAttribute('data-variant', 'outline');
        });

        it('should render ghost variant', () => {
            render(<Button variant="ghost">Ghost</Button>);
            expect(screen.getByRole('button')).toHaveAttribute('data-variant', 'ghost');
        });
    });

    describe('Sizes', () => {
        it('should render small size', () => {
            render(<Button size="sm">Small</Button>);
            expect(screen.getByRole('button')).toHaveAttribute('data-size', 'sm');
        });

        it('should render large size', () => {
            render(<Button size="lg">Large</Button>);
            expect(screen.getByRole('button')).toHaveAttribute('data-size', 'lg');
        });

        it('should render icon size', () => {
            render(<Button size="icon">🔍</Button>);
            expect(screen.getByRole('button')).toHaveAttribute('data-size', 'icon');
        });
    });

    describe('States', () => {
        it('should be disabled when disabled prop is true', () => {
            render(<Button disabled>Disabled</Button>);
            expect(screen.getByRole('button')).toBeDisabled();
        });

        it('should pass through HTML button props', () => {
            render(<Button type="submit" id="test-btn">Submit</Button>);
            const button = screen.getByRole('button');
            expect(button).toHaveAttribute('type', 'submit');
            expect(button).toHaveAttribute('id', 'test-btn');
        });
    });

    describe('Interactions', () => {
        it('should call onClick when clicked', async () => {
            const user = userEvent.setup();
            const handleClick = vi.fn();

            render(<Button onClick={handleClick}>Click</Button>);
            await user.click(screen.getByRole('button'));

            expect(handleClick).toHaveBeenCalledTimes(1);
        });

        it('should not call onClick when disabled', async () => {
            const user = userEvent.setup();
            const handleClick = vi.fn();

            render(<Button disabled onClick={handleClick}>Click</Button>);
            await user.click(screen.getByRole('button'));

            expect(handleClick).not.toHaveBeenCalled();
        });
    });
});
