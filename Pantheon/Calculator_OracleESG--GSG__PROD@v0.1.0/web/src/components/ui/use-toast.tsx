// Simple toast hook for MVP
import React from "react"

type Toast = {
  id: string
  title?: string
  description?: string
  action?: React.ReactNode
  variant?: "default" | "destructive"
}

let toastId = 0

export function useToast() {
  const toast = ({ title, description, variant }: Omit<Toast, "id">) => {
    // Simple console log for MVP - in real app would show UI toast
    const level = variant === "destructive" ? "error" : "info"
    console[level](`Toast: ${title}${description ? ` - ${description}` : ""}`)
  }

  return {
    toast,
    toasts: [] as Toast[]
  }
}

// Placeholder components for toast
export function Toast({ children }: { children: React.ReactNode }) {
  return <div>{children}</div>
}

export function ToastTitle({ children }: { children: React.ReactNode }) {
  return <div>{children}</div>
}

export function ToastDescription({ children }: { children: React.ReactNode }) {
  return <div>{children}</div>
}

export function ToastProvider({ children }: { children: React.ReactNode }) {
  return <div>{children}</div>
}

export function ToastClose() {
  return <button>×</button>
}

export function ToastViewport() {
  return <div />
}