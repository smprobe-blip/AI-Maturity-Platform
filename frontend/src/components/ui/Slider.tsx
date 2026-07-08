import React from 'react';
import { cn } from '@/utils/cn';

interface SliderProps {
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
  label?: string;
  description?: string;
}

export const Slider: React.FC<SliderProps> = ({
  value,
  onChange,
  min = 1,
  max = 5,
  step = 1,
  label,
  description,
}) => {
  const marks = Array.from({ length: max - min + 1 }, (_, i) => min + i);

  return (
    <div className="w-full">
      {label && (
        <div className="mb-3">
          <label className="block text-sm font-semibold text-gray-900">{label}</label>
          {description && (
            <p className="text-xs text-gray-500 mt-1">{description}</p>
          )}
        </div>
      )}
      
      <div className="relative">
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
        />
        
        <div className="flex justify-between mt-2 text-xs text-gray-600">
          {marks.map((mark) => (
            <span
              key={mark}
              className={cn(
                'font-medium',
                value === mark ? 'text-primary-600 font-bold' : ''
              )}
            >
              {mark}
            </span>
          ))}
        </div>
      </div>
      
      <div className="mt-2 text-center">
        <span className="inline-block px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm font-semibold">
          Оценка: {value} / {max}
        </span>
      </div>
    </div>
  );
};