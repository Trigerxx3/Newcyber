# PDF Preview for Generate PDF Button

## Problem
The "Generate PDF" button (cyan button with download icon) in the Investigation Reports section was directly downloading the PDF without showing a preview first. Users wanted to be able to preview the PDF before downloading it.

## Solution Implemented

### 1. **Added PDF Preview State Variables**
```typescript
const [pdfPreviewUrl, setPdfPreviewUrl] = useState<string | null>(null)
const [showPdfPreviewDialog, setShowPdfPreviewDialog] = useState(false)
const [pdfGenerating, setPdfGenerating] = useState(false)
```

### 2. **Created PDF Preview Functions**

#### **`generateAndPreviewPdf(caseId: number)`**
- Generates the PDF report
- Creates an object URL for preview
- Opens the preview dialog
- Shows success toast

#### **`downloadPdfFromPreview()`**
- Downloads the PDF from the preview URL
- Uses the same filename format as the original function
- Shows download confirmation toast

#### **`closePdfPreview()`**
- Revokes the object URL to free memory
- Closes the preview dialog
- Cleans up state

### 3. **Updated Generate PDF Button**
```typescript
<Button
  className="bg-primary hover:bg-primary/90"
  onClick={() => {
    if (activeCase?.id) generateAndPreviewPdf(activeCase.id)
  }}
  disabled={pdfGenerating}
>
  {pdfGenerating ? <Loader2 className="h-4 w-4 animate-spin" /> : <Download className="h-4 w-4" />}
  <span className="ml-2">Generate PDF</span>
</Button>
```

### 4. **Added PDF Preview Dialog**
- **Large dialog** (max-w-6xl) to accommodate PDF preview
- **PDF iframe** for displaying the PDF content
- **Header** with case title and description
- **Footer** with Close and Download buttons
- **Responsive design** with proper height constraints

## How It Works Now

### ✅ **PDF Preview Workflow**
1. **Click "Generate PDF" button** (cyan button with download icon)
2. **PDF is generated** in the background
3. **Preview dialog opens** showing the PDF in an iframe
4. **Review the PDF** content before downloading
5. **Click "Download PDF"** to save the file
6. **Click "Close Preview"** to cancel without downloading

### 🎯 **Enhanced User Experience**
- **Preview before download** - Users can see the PDF content first
- **Large preview window** - Full PDF content is visible
- **Download confirmation** - Clear download button in the preview
- **Memory management** - Object URLs are properly cleaned up
- **Loading states** - Shows spinner while generating PDF
- **Error handling** - Proper error messages if PDF generation fails

### 📱 **Dialog Features**
- **Responsive design** - Works on different screen sizes
- **Full PDF view** - 70vh height for comfortable viewing
- **Case title** - Shows which case the PDF is for
- **Clear actions** - Separate buttons for close and download
- **Proper cleanup** - Memory is freed when dialog closes

## Files Modified

### **`cyber/src/app/dashboard/reports/page.tsx`**
- ✅ Added PDF preview state variables
- ✅ Created `generateAndPreviewPdf` function
- ✅ Created `downloadPdfFromPreview` function
- ✅ Created `closePdfPreview` function
- ✅ Updated Generate PDF button to use preview
- ✅ Added PDF preview dialog component
- ✅ Added proper loading states and error handling

## Testing

### 1. **Test PDF Preview**
1. Go to Investigation Reports page
2. Make sure you have an active case selected
3. Click the "Generate PDF" button (cyan button)
4. Verify the preview dialog opens
5. Check that the PDF is displayed in the iframe
6. Verify the case title is shown in the dialog header

### 2. **Test PDF Download**
1. In the preview dialog, click "Download PDF"
2. Verify the PDF downloads with the correct filename
3. Check that the download confirmation toast appears

### 3. **Test Dialog Close**
1. In the preview dialog, click "Close Preview"
2. Verify the dialog closes without downloading
3. Check that memory is properly cleaned up

### 4. **Test Error Handling**
1. Try generating PDF with invalid case ID
2. Verify error toast appears
3. Check that loading state is properly reset

## Benefits

### ✅ **User Experience**
- **Preview before download** - Users can verify content before saving
- **No accidental downloads** - Users can cancel if not satisfied
- **Better workflow** - Review → Download instead of direct download
- **Memory efficient** - Object URLs are properly managed

### ✅ **Functionality**
- **Same PDF generation** - Uses the same backend endpoint
- **Same filename format** - Maintains consistent naming
- **Error handling** - Proper error messages and recovery
- **Loading states** - Clear feedback during generation

### ✅ **Technical**
- **Memory management** - Object URLs are revoked properly
- **State management** - Clean state updates and cleanup
- **Responsive design** - Works on all screen sizes
- **Accessibility** - Proper ARIA labels and keyboard navigation

## Status
- ✅ PDF preview functionality implemented
- ✅ Generate PDF button updated to show preview
- ✅ PDF preview dialog with iframe display
- ✅ Download functionality from preview
- ✅ Proper memory management
- ✅ Error handling and loading states
- ✅ No linting errors

The "Generate PDF" button now shows a preview of the PDF before allowing users to download it, providing a much better user experience for reviewing reports before saving them.
