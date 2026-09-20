import React from 'react';
import { clsx } from 'clsx';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, className, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-capco-gray-700 mb-1">
            {label}
            {props.required && <span className="text-capco-red ml-1">*</span>}
          </label>
        )}
        <input
          ref={ref}
          className={clsx(
            'input',
            error && 'border-capco-red focus:ring-capco-red',
            className
          )}
          {...props}
        />
        {error && (
          <p className="mt-1 text-sm text-capco-red">{error}</p>
        )}
        {helperText && !error && (
          <p className="mt-1 text-sm text-capco-gray-500">{helperText}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

interface TextAreaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const TextArea = React.forwardRef<HTMLTextAreaElement, TextAreaProps>(
  ({ label, error, helperText, className, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-capco-gray-700 mb-1">
            {label}
            {props.required && <span className="text-capco-red ml-1">*</span>}
          </label>
        )}
        <textarea
          ref={ref}
          className={clsx(
            'input min-h-[100px]',
            error && 'border-capco-red focus:ring-capco-red',
            className
          )}
          {...props}
        />
        {error && (
          <p className="mt-1 text-sm text-capco-red">{error}</p>
        )}
        {helperText && !error && (
          <p className="mt-1 text-sm text-capco-gray-500">{helperText}</p>
        )}
      </div>
    );
  }
);

TextArea.displayName = 'TextArea';

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  helperText?: string;
  options: { value: string; label: string }[];
}

export const Select = React.forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, error, helperText, options, className, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-capco-gray-700 mb-1">
            {label}
            {props.required && <span className="text-capco-red ml-1">*</span>}
          </label>
        )}
        <select
          ref={ref}
          className={clsx(
            'input',
            error && 'border-capco-red focus:ring-capco-red',
            className
          )}
          {...props}
        >
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        {error && (
          <p className="mt-1 text-sm text-capco-red">{error}</p>
        )}
        {helperText && !error && (
          <p className="mt-1 text-sm text-capco-gray-500">{helperText}</p>
        )}
      </div>
    );
  }
);

Select.displayName = 'Select';
