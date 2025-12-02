import { ComponentPropsWithoutRef, forwardRef } from 'react';
import { motion } from 'framer-motion';

interface NeonButtonProps extends ComponentPropsWithoutRef<'button'> {
  variant?: 'primary' | 'secondary' | 'accent';
  size?: 'sm' | 'md' | 'lg';
  glow?: boolean;
}

export const NeonButton = forwardRef<HTMLButtonElement, NeonButtonProps>(
  ({ variant = 'primary', size = 'md', glow = true, className = '', children, ...props }, ref) => {
    const baseClasses = 'rounded-lg font-medium transition-all duration-300 focus:outline-none';
    const sizeClasses = {
      sm: 'px-3 py-1.5 text-sm',
      md: 'px-4 py-2 text-base',
      lg: 'px-6 py-3 text-lg',
    };
    const variantClasses = {
      primary: 'bg-dark-700 text-neon-primary hover:bg-dark-600 border border-neon-primary',
      secondary: 'bg-dark-700 text-neon-secondary hover:bg-dark-600 border border-neon-secondary',
      accent: 'bg-dark-700 text-neon-accent hover:bg-dark-600 border border-neon-accent',
    };
    const glowEffect = glow
      ? {
          primary: 'hover:shadow-lg hover:shadow-neon-primary/30',
          secondary: 'hover:shadow-lg hover:shadow-neon-secondary/30',
          accent: 'hover:shadow-lg hover:shadow-neon-accent/30',
        }[variant]
      : '';

    return (
      <motion.button
        ref={ref}
        whileHover={{ scale: 1.03 }}
        whileTap={{ scale: 0.98 }}
        className={`${baseClasses} ${sizeClasses[size]} ${variantClasses[variant]} ${glowEffect} ${className}`}
        {...props}
      >
        {children}
      </motion.button>
    );
  }
);

NeonButton.displayName = 'NeonButton';
