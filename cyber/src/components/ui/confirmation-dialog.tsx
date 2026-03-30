'use client'

import { useState } from 'react'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { 
  AlertTriangle, 
  Trash2, 
  Archive, 
  XCircle, 
  UserX, 
  Shield, 
  FileText,
  Database,
  Link,
  Unlink
} from 'lucide-react'

interface ConfirmationDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onConfirm: () => void | Promise<void>
  title: string
  description: string
  confirmText?: string
  cancelText?: string
  variant?: 'destructive' | 'warning' | 'info'
  icon?: React.ReactNode
  requireNotes?: boolean
  notesLabel?: string
  notesPlaceholder?: string
  notesValue?: string
  onNotesChange?: (notes: string) => void
  isLoading?: boolean
  itemName?: string
  itemType?: string
}

export function ConfirmationDialog({
  open,
  onOpenChange,
  onConfirm,
  title,
  description,
  confirmText = "Confirm",
  cancelText = "Cancel",
  variant = 'destructive',
  icon,
  requireNotes = false,
  notesLabel = "Notes",
  notesPlaceholder = "Enter additional notes...",
  notesValue = "",
  onNotesChange,
  isLoading = false,
  itemName,
  itemType
}: ConfirmationDialogProps) {
  const [notes, setNotes] = useState(notesValue)

  const handleConfirm = async () => {
    if (requireNotes && !notes.trim()) {
      return
    }
    
    if (onNotesChange) {
      onNotesChange(notes)
    }
    
    await onConfirm()
    setNotes('')
  }

  const getIcon = () => {
    if (icon) return icon
    
    switch (variant) {
      case 'destructive':
        return <Trash2 className="h-6 w-6 text-red-500" />
      case 'warning':
        return <AlertTriangle className="h-6 w-6 text-orange-500" />
      case 'info':
        return <Shield className="h-6 w-6 text-blue-500" />
      default:
        return <AlertTriangle className="h-6 w-6 text-orange-500" />
    }
  }

  const getVariantStyles = () => {
    switch (variant) {
      case 'destructive':
        return {
          button: 'bg-red-600 hover:bg-red-700 text-white',
          border: 'border-red-200',
          text: 'text-red-800'
        }
      case 'warning':
        return {
          button: 'bg-orange-600 hover:bg-orange-700 text-white',
          border: 'border-orange-200',
          text: 'text-orange-800'
        }
      case 'info':
        return {
          button: 'bg-blue-600 hover:bg-blue-700 text-white',
          border: 'border-blue-200',
          text: 'text-blue-800'
        }
      default:
        return {
          button: 'bg-red-600 hover:bg-red-700 text-white',
          border: 'border-red-200',
          text: 'text-red-800'
        }
    }
  }

  const styles = getVariantStyles()

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent className="max-w-md">
        <AlertDialogHeader>
          <div className="flex items-center gap-3">
            {getIcon()}
            <AlertDialogTitle className="text-lg font-semibold">
              {title}
            </AlertDialogTitle>
          </div>
          <AlertDialogDescription className="text-sm text-muted-foreground">
            {description}
          </AlertDialogDescription>
        </AlertDialogHeader>

        {/* Item Information */}
        {(itemName || itemType) && (
          <div className={`p-3 rounded-lg border ${styles.border} bg-gray-50`}>
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">Item:</span>
              <Badge variant="outline" className="text-xs">
                {itemType}
              </Badge>
            </div>
            <div className="text-sm font-medium mt-1">{itemName}</div>
          </div>
        )}

        {/* Notes Field */}
        {requireNotes && (
          <div className="space-y-2">
            <Label htmlFor="confirmation-notes" className="text-sm font-medium">
              {notesLabel} <span className="text-red-500">*</span>
            </Label>
            <Textarea
              id="confirmation-notes"
              placeholder={notesPlaceholder}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="min-h-[80px]"
              required
            />
            {requireNotes && !notes.trim() && (
              <p className="text-xs text-red-500">Notes are required for this action</p>
            )}
          </div>
        )}

        <AlertDialogFooter className="gap-2">
          <AlertDialogCancel asChild>
            <Button variant="outline" disabled={isLoading}>
              {cancelText}
            </Button>
          </AlertDialogCancel>
          <AlertDialogAction asChild>
            <Button
              onClick={handleConfirm}
              disabled={isLoading || (requireNotes && !notes.trim())}
              className={styles.button}
            >
              {isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Processing...
                </>
              ) : (
                confirmText
              )}
            </Button>
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}

// Predefined confirmation dialogs for common actions
export function DeleteConfirmationDialog({
  open,
  onOpenChange,
  onConfirm,
  itemName,
  itemType = "Item",
  isLoading = false
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  onConfirm: () => void | Promise<void>
  itemName: string
  itemType?: string
  isLoading?: boolean
}) {
  return (
    <ConfirmationDialog
      open={open}
      onOpenChange={onOpenChange}
      onConfirm={onConfirm}
      title="Delete Item"
      description="This action cannot be undone. The item will be permanently removed from the system."
      confirmText="Delete"
      variant="destructive"
      itemName={itemName}
      itemType={itemType}
      isLoading={isLoading}
    />
  )
}

export function ArchiveConfirmationDialog({
  open,
  onOpenChange,
  onConfirm,
  itemName,
  itemType = "Item",
  isLoading = false,
  requireNotes = true
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  onConfirm: (notes: string) => void | Promise<void>
  itemName: string
  itemType?: string
  isLoading?: boolean
  requireNotes?: boolean
}) {
  const [notes, setNotes] = useState('')

  const handleConfirm = async () => {
    await onConfirm(notes)
    setNotes('')
  }

  return (
    <ConfirmationDialog
      open={open}
      onOpenChange={onOpenChange}
      onConfirm={handleConfirm}
      title="Archive Item"
      description="This item will be moved to the archive. You can restore it later if needed."
      confirmText="Archive"
      variant="warning"
      icon={<Archive className="h-6 w-6 text-orange-500" />}
      itemName={itemName}
      itemType={itemType}
      isLoading={isLoading}
      requireNotes={requireNotes}
      notesLabel="Archive Notes"
      notesPlaceholder="Enter reason for archiving..."
      notesValue={notes}
      onNotesChange={setNotes}
    />
  )
}

export function CloseConfirmationDialog({
  open,
  onOpenChange,
  onConfirm,
  itemName,
  itemType = "Case",
  isLoading = false,
  requireNotes = true
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  onConfirm: (notes: string) => void | Promise<void>
  itemName: string
  itemType?: string
  isLoading?: boolean
  requireNotes?: boolean
}) {
  const [notes, setNotes] = useState('')

  const handleConfirm = async () => {
    await onConfirm(notes)
    setNotes('')
  }

  return (
    <ConfirmationDialog
      open={open}
      onOpenChange={onOpenChange}
      onConfirm={handleConfirm}
      title="Close Item"
      description="This item will be marked as closed. You can archive it later if needed."
      confirmText="Close"
      variant="warning"
      icon={<XCircle className="h-6 w-6 text-orange-500" />}
      itemName={itemName}
      itemType={itemType}
      isLoading={isLoading}
      requireNotes={requireNotes}
      notesLabel="Close Notes"
      notesPlaceholder="Enter reason for closing..."
      notesValue={notes}
      onNotesChange={setNotes}
    />
  )
}

export function ToggleStatusConfirmationDialog({
  open,
  onOpenChange,
  onConfirm,
  itemName,
  itemType = "User",
  currentStatus,
  newStatus,
  isLoading = false
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  onConfirm: () => void | Promise<void>
  itemName: string
  itemType?: string
  currentStatus: string
  newStatus: string
  isLoading?: boolean
}) {
  return (
    <ConfirmationDialog
      open={open}
      onOpenChange={onOpenChange}
      onConfirm={onConfirm}
      title={`${newStatus === 'active' ? 'Activate' : 'Deactivate'} ${itemType}`}
      description={`This will ${newStatus === 'active' ? 'activate' : 'deactivate'} the ${itemType.toLowerCase()}.`}
      confirmText={newStatus === 'active' ? 'Activate' : 'Deactivate'}
      variant={newStatus === 'active' ? 'info' : 'warning'}
      icon={newStatus === 'active' ? 
        <UserX className="h-6 w-6 text-green-500" /> : 
        <UserX className="h-6 w-6 text-orange-500" />
      }
      itemName={itemName}
      itemType={itemType}
      isLoading={isLoading}
    />
  )
}

export function LinkContentConfirmationDialog({
  open,
  onOpenChange,
  onConfirm,
  itemCount,
  caseName,
  isLoading = false
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  onConfirm: () => void | Promise<void>
  itemCount: number
  caseName: string
  isLoading?: boolean
}) {
  return (
    <ConfirmationDialog
      open={open}
      onOpenChange={onOpenChange}
      onConfirm={onConfirm}
      title="Link Content to Case"
      description={`This will link ${itemCount} content item${itemCount !== 1 ? 's' : ''} to the case.`}
      confirmText="Link Content"
      variant="info"
      icon={<Link className="h-6 w-6 text-blue-500" />}
      itemName={caseName}
      itemType="Case"
      isLoading={isLoading}
    />
  )
}

export function UnlinkContentConfirmationDialog({
  open,
  onOpenChange,
  onConfirm,
  itemName,
  caseName,
  isLoading = false
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  onConfirm: () => void | Promise<void>
  itemName: string
  caseName: string
  isLoading?: boolean
}) {
  return (
    <ConfirmationDialog
      open={open}
      onOpenChange={onOpenChange}
      onConfirm={onConfirm}
      title="Unlink Content"
      description="This will remove the content from the case. The content will remain in the system."
      confirmText="Unlink"
      variant="warning"
      icon={<Unlink className="h-6 w-6 text-orange-500" />}
      itemName={itemName}
      itemType="Content"
      isLoading={isLoading}
    />
  )
}



