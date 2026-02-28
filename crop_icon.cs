using System;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Drawing.Imaging;

public class ImageCropper
{
    public static void CropToCircle(string inputPath, string outputPath)
    {
        using (Bitmap orig = new Bitmap(inputPath))
        {
            // Find bounding box of non-white pixels
            int minX = orig.Width, minY = orig.Height, maxX = 0, maxY = 0;
            // To speed up, we can lock bits, but for a simple logo, GetPixel is acceptable if small, 
            // but let's just do a basic scan
            // Better: just use a reasonable heuristic or lock bits. Let's assume the logo is somewhat centered.
            // Actually, for safety with any resolution, let's use a fast unsafe method or just a step-based scan.
            
            // Fast scan with step 2
            for (int y = 0; y < orig.Height; y += 2)
            {
                for (int x = 0; x < orig.Width; x += 2)
                {
                    Color c = orig.GetPixel(x, y);
                    // if not white and not transparent
                    if (c.A > 10 && (c.R < 250 || c.G < 250 || c.B < 250))
                    {
                        if (x < minX) minX = x;
                        if (x > maxX) maxX = x;
                        if (y < minY) minY = y;
                        if (y > maxY) maxY = y;
                    }
                }
            }

            // Fallback if no non-white found
            if (minX > maxX || minY > maxY)
            {
                minX = 0; minY = 0; maxX = orig.Width - 1; maxY = orig.Height - 1;
            }

            // Pad the bounding box a bit
            int pad = 10;
            minX = Math.Max(0, minX - pad);
            minY = Math.Max(0, minY - pad);
            maxX = Math.Min(orig.Width - 1, maxX + pad);
            maxY = Math.Min(orig.Height - 1, maxY + pad);

            int bWidth = maxX - minX + 1;
            int bHeight = maxY - minY + 1;
            
            // We want a perfect square
            int size = Math.Max(bWidth, bHeight);

            using (Bitmap square = new Bitmap(size, size, PixelFormat.Format32bppArgb))
            {
                using (Graphics g = Graphics.FromImage(square))
                {
                    g.Clear(Color.Transparent);
                    g.SmoothingMode = SmoothingMode.AntiAlias;

                    // Create circle path
                    GraphicsPath path = new GraphicsPath();
                    path.AddEllipse(0, 0, size, size);
                    g.SetClip(path);

                    // Draw the cropped portion centered
                    int dstX = (size - bWidth) / 2;
                    int dstY = (size - bHeight) / 2;
                    
                    Rectangle srcRect = new Rectangle(minX, minY, bWidth, bHeight);
                    Rectangle dstRect = new Rectangle(dstX, dstY, bWidth, bHeight);
                    
                    g.DrawImage(orig, dstRect, srcRect, GraphicsUnit.Pixel);
                }

                // Resize to 512x512
                using (Bitmap resized = new Bitmap(512, 512, PixelFormat.Format32bppArgb))
                {
                    using (Graphics g2 = Graphics.FromImage(resized))
                    {
                        g2.SmoothingMode = SmoothingMode.AntiAlias;
                        g2.InterpolationMode = InterpolationMode.HighQualityBicubic;
                        g2.DrawImage(square, 0, 0, 512, 512);
                    }
                    resized.Save(outputPath, ImageFormat.Png);
                }
            }
        }
    }
}
