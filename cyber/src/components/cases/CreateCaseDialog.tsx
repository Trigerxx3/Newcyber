'use client'

import { useState, useEffect } from 'react'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { X, Plus, AlertTriangle, CheckCircle, Clock } from 'lucide-react'
import apiClient from '@/lib/api'
import { toast } from '@/hooks/use-toast'

interface CreateCaseDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onCreateCase: (caseData: any) => void
}

export default function CreateCaseDialog({ open, onOpenChange, onCreateCase }: CreateCaseDialogProps) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    type: 'drug_trafficking_investigation',
    priority: 'medium',
    summary: '',
    objectives: '',
    methodology: '',
    tags: [] as string[]
  })
  const [newTag, setNewTag] = useState('')
  const [loading, setLoading] = useState(false)
  const [canCreate, setCanCreate] = useState(true)
  const [permissionMessage, setPermissionMessage] = useState('')
  const [checkingPermission, setCheckingPermission] = useState(false)
  const [validationErrors, setValidationErrors] = useState<{[key: string]: string}>({})

  // Check case creation permissions when dialog opens
  useEffect(() => {
    if (open) {
      checkCaseCreationPermission()
    }
  }, [open])

  // Validation functions
  const containsNumbers = (text: string): boolean => {
    return /\d/.test(text)
  }

  const validateTextField = (fieldName: string, value: string): string => {
    if (!value.trim()) {
      return fieldName === 'title' ? 'This field is required' : ''
    }
    
    if (containsNumbers(value)) {
      return 'Numbers are not allowed. Please use only letters, spaces, and punctuation.'
    }
    
    if (value.length < 3) {
      return 'Must be at least 3 characters long'
    }
    
    if (value.length > 200) {
      return 'Must be less than 200 characters'
    }
    
    return ''
  }

  const validateTextArea = (fieldName: string, value: string): string => {
    if (!value.trim()) {
      return fieldName === 'title' ? 'This field is required' : ''
    }
    
    if (containsNumbers(value)) {
      return 'Numbers are not allowed. Please use only letters, spaces, and punctuation.'
    }
    
    if (value.length < 10) {
      return 'Must be at least 10 characters long'
    }
    
    if (value.length > 1000) {
      return 'Must be less than 1000 characters'
    }
    
    return ''
  }

  const validateTag = (tag: string): string => {
    if (!tag.trim()) {
      return 'Tag cannot be empty'
    }
    
    if (containsNumbers(tag)) {
      return 'Numbers are not allowed in tags'
    }
    
    if (tag.length < 2) {
      return 'Tag must be at least 2 characters long'
    }
    
    if (tag.length > 20) {
      return 'Tag must be less than 20 characters'
    }
    
    return ''
  }

  const handleFieldChange = (fieldName: string, value: string) => {
    setFormData(prev => ({ ...prev, [fieldName]: value }))
    
    // Clear validation error when user starts typing
    if (validationErrors[fieldName]) {
      setValidationErrors(prev => ({ ...prev, [fieldName]: '' }))
    }
  }

  const handleInputChange = (fieldName: string, value: string) => {
    // Filter out numbers in real-time
    const filteredValue = value.replace(/\d/g, '')
    handleFieldChange(fieldName, filteredValue)
  }

  const handleTagInputChange = (value: string) => {
    // Filter out numbers in real-time for tags
    const filteredValue = value.replace(/\d/g, '')
    setNewTag(filteredValue)
  }

  const validateForm = (): boolean => {
    const errors: {[key: string]: string} = {}
    
    // Validate title
    const titleError = validateTextField('title', formData.title)
    if (titleError) errors.title = titleError
    
    // Validate description
    const descriptionError = validateTextArea('description', formData.description)
    if (descriptionError) errors.description = descriptionError
    
    // Validate summary
    const summaryError = validateTextArea('summary', formData.summary)
    if (summaryError) errors.summary = summaryError
    
    // Validate objectives
    const objectivesError = validateTextArea('objectives', formData.objectives)
    if (objectivesError) errors.objectives = objectivesError
    
    // Validate methodology
    const methodologyError = validateTextArea('methodology', formData.methodology)
    if (methodologyError) errors.methodology = methodologyError
    
    // Validate tags
    formData.tags.forEach((tag, index) => {
      const tagError = validateTag(tag)
      if (tagError) errors[`tag_${index}`] = tagError
    })
    
    setValidationErrors(errors)
    return Object.keys(errors).length === 0
  }

  const checkCaseCreationPermission = async () => {
    try {
      setCheckingPermission(true)
      const response = await apiClient.canCreateCase() as any
      
      if (response.status === 'success') {
        setCanCreate(response.can_create)
        setPermissionMessage(response.message)
      } else {
        setCanCreate(false)
        setPermissionMessage('Unable to check permissions')
      }
    } catch (error) {
      console.error('Error checking case creation permission:', error)
      setCanCreate(false)
      setPermissionMessage('Error checking permissions')
    } finally {
      setCheckingPermission(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Validate form before submission
    if (!validateForm()) {
      toast({
        title: "Validation Error",
        description: "Please fix the errors in the form before submitting.",
        variant: "destructive"
      })
      return
    }
    
    setLoading(true)

    try {
      const response = await onCreateCase(formData) as any
      
      // Handle case request submission
      if (response && response.requires_approval) {
        toast({
          title: "Case Request Submitted",
          description: `Your case request has been submitted for admin approval. Request ID: ${response.request_id}`,
          variant: "default"
        })
      } else if (response && response.status === 'success') {
        toast({
          title: "Case Created Successfully",
          description: "Your new case has been created and is ready for investigation.",
          variant: "default"
        })
      }
      
      // Reset form
      setFormData({
        title: '',
        description: '',
        type: 'drug_trafficking_investigation',
        priority: 'medium',
        summary: '',
        objectives: '',
        methodology: '',
        tags: []
      })
    } catch (error) {
      console.error('Error creating case/request:', error)
      toast({
        title: "Error",
        description: "Failed to create case or submit request. Please try again.",
        variant: "destructive"
      })
    } finally {
      setLoading(false)
    }
  }

  const addTag = () => {
    const trimmedTag = newTag.trim()
    const tagError = validateTag(trimmedTag)
    
    if (tagError) {
      toast({
        title: "Invalid Tag",
        description: tagError,
        variant: "destructive"
      })
      return
    }
    
    if (trimmedTag && !formData.tags.includes(trimmedTag)) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, trimmedTag]
      }))
      setNewTag('')
    }
  }

  const removeTag = (tagToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }))
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      addTag()
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Create New Case</DialogTitle>
          <DialogDescription>
            Create a new investigation case to track drug-related content and suspicious activities on social media platforms.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Permission Status Alert */}
          {checkingPermission ? (
            <Alert>
              <Clock className="h-4 w-4" />
              <AlertDescription>
                Checking case creation permissions...
              </AlertDescription>
            </Alert>
          ) : !canCreate ? (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                <div className="space-y-2">
                  <p>{permissionMessage}</p>
                  <p className="text-sm">
                    <strong>What happens next?</strong> Your case request will be submitted for admin approval. 
                    You'll be notified once it's reviewed.
                  </p>
                </div>
              </AlertDescription>
            </Alert>
          ) : (
            <Alert className="border-green-200 bg-green-50">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-800">
                {permissionMessage || "You can create a new case directly."}
              </AlertDescription>
            </Alert>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="title">Case Title *</Label>
              <Input
                id="title"
                value={formData.title}
                onChange={(e) => handleInputChange('title', e.target.value)}
                placeholder="e.g., Drug trafficking investigation - Instagram user @suspicious_user"
                className={validationErrors.title ? 'border-red-500 focus:border-red-500' : ''}
                required
              />
              {validationErrors.title && (
                <p className="text-red-500 text-sm">{validationErrors.title}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="type">Case Type</Label>
              <Select value={formData.type} onValueChange={(value) => setFormData(prev => ({ ...prev, type: value }))}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="drug_trafficking_investigation">Drug Trafficking Investigation</SelectItem>
                  <SelectItem value="substance_abuse_detection">Substance Abuse Detection</SelectItem>
                  <SelectItem value="social_media_monitoring">Social Media Monitoring</SelectItem>
                  <SelectItem value="suspicious_content_analysis">Suspicious Content Analysis</SelectItem>
                  <SelectItem value="user_behavior_analysis">User Behavior Analysis</SelectItem>
                  <SelectItem value="network_disruption">Network Disruption</SelectItem>
                  <SelectItem value="compliance_enforcement">Compliance Enforcement</SelectItem>
                  <SelectItem value="osint_investigation">OSINT Investigation</SelectItem>
                  <SelectItem value="custom">Custom</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              placeholder="Brief description of the drug-related content or suspicious activity to be investigated..."
              className={validationErrors.description ? 'border-red-500 focus:border-red-500' : ''}
              rows={3}
            />
            {validationErrors.description && (
              <p className="text-red-500 text-sm">{validationErrors.description}</p>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="priority">Priority</Label>
              <Select value={formData.priority} onValueChange={(value) => setFormData(prev => ({ ...prev, priority: value }))}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Low</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="critical">Critical</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="tags">Tags</Label>
              <div className="flex gap-2">
                <Input
                  value={newTag}
                  onChange={(e) => handleTagInputChange(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Add a tag..."
                  className="flex-1"
                />
                <Button type="button" variant="outline" onClick={addTag} disabled={!newTag.trim()}>
                  <Plus className="w-4 h-4" />
                </Button>
              </div>
              {formData.tags.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {formData.tags.map((tag, index) => (
                    <div key={tag} className="flex items-center gap-1">
                      <Badge variant="secondary" className="flex items-center gap-1">
                        {tag}
                        <button
                          type="button"
                          onClick={() => removeTag(tag)}
                          className="hover:bg-destructive/20 rounded-full p-0.5"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </Badge>
                      {validationErrors[`tag_${index}`] && (
                        <span className="text-red-500 text-xs">{validationErrors[`tag_${index}`]}</span>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="summary">Initial Summary</Label>
            <Textarea
              id="summary"
              value={formData.summary}
              onChange={(e) => handleInputChange('summary', e.target.value)}
              placeholder="Initial summary of the drug-related investigation and what has been discovered so far..."
              className={validationErrors.summary ? 'border-red-500 focus:border-red-500' : ''}
              rows={3}
            />
            {validationErrors.summary && (
              <p className="text-red-500 text-sm">{validationErrors.summary}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="objectives">Objectives</Label>
            <Textarea
              id="objectives"
              value={formData.objectives}
              onChange={(e) => handleInputChange('objectives', e.target.value)}
              placeholder="What are the main objectives of this drug-related investigation?"
              className={validationErrors.objectives ? 'border-red-500 focus:border-red-500' : ''}
              rows={3}
            />
            {validationErrors.objectives && (
              <p className="text-red-500 text-sm">{validationErrors.objectives}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="methodology">Methodology</Label>
            <Textarea
              id="methodology"
              value={formData.methodology}
              onChange={(e) => handleInputChange('methodology', e.target.value)}
              placeholder="Describe the drug content analysis methodology and tools to be used..."
              className={validationErrors.methodology ? 'border-red-500 focus:border-red-500' : ''}
              rows={3}
            />
            {validationErrors.methodology && (
              <p className="text-red-500 text-sm">{validationErrors.methodology}</p>
            )}
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)} disabled={loading}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading || !formData.title.trim()}>
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  {canCreate ? 'Creating Case...' : 'Submitting Request...'}
                </>
              ) : (
                canCreate ? 'Create Case' : 'Submit Request for Admin Approval'
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
