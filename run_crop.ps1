$imgPath = "C:\Users\marco\.gemini\antigravity\brain\52011f59-787f-4e5d-a56d-60f3ce390419\media__1772303463347.png"
$outputPath = "c:\Users\marco\Documents\GitHub\ilpolimate\assets\icons\logo-circle.png"

Add-Type -TypeDefinition (Get-Content -Raw -Path "c:\Users\marco\Documents\GitHub\ilpolimate\crop_icon.cs") -ReferencedAssemblies System.Drawing

[ImageCropper]::CropToCircle($imgPath, $outputPath)
Write-Output "Image cropped successfully!"
