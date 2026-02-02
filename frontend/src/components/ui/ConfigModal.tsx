import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';

interface ConfigModalProps {
    isOpen: boolean;
    onClose: () => void;
    title: string;
    description?: string;
    icon?: React.ReactNode;
    children: React.ReactNode;
}

export const ConfigModal: React.FC<ConfigModalProps> = ({ isOpen, onClose, title, description, icon, children }) => {
    // Prevent scrolling when modal is open
    React.useEffect(() => {
        if (isOpen) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = 'unset';
        }
        return () => {
            document.body.style.overflow = 'unset';
        };
    }, [isOpen]);

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 transition-colors"
                    />

                    {/* Modal Content */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 20 }}
                        transition={{ duration: 0.2, ease: "easeOut" }}
                        className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 pointer-events-none"
                    >
                        <div
                            className="bg-white pointer-events-auto w-full max-w-2xl max-h-[90vh] rounded-2xl shadow-xl overflow-hidden flex flex-col"
                            onClick={(e) => e.stopPropagation()}
                        >
                            {/* Header */}
                            <div className="flex items-start justify-between p-6 border-b border-zinc-100 bg-zinc-50/50">
                                <div className="flex gap-4">
                                    {icon && (
                                        <div className="p-3 bg-white rounded-xl shadow-sm border border-zinc-100 text-primary">
                                            {icon}
                                        </div>
                                    )}
                                    <div className="space-y-1">
                                        <h2 className="text-xl font-semibold text-zinc-900">{title}</h2>
                                        {description && (
                                            <p className="text-sm text-zinc-500 max-w-sm">{description}</p>
                                        )}
                                    </div>
                                </div>
                                <button
                                    onClick={onClose}
                                    className="p-2 rounded-lg hover:bg-zinc-100 text-zinc-400 hover:text-zinc-600 transition-colors"
                                >
                                    <X className="w-5 h-5" />
                                </button>
                            </div>

                            {/* Body */}
                            <div className="p-6 overflow-y-auto">
                                {children}
                            </div>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
};
