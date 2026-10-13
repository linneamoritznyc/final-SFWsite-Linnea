# Replicate prompt: the Open House house graphic

Run this in Claude Code on your own computer (that is where the Replicate token lives).

**Model:** `google/nano-banana` (image edit). Pass `replicate-house-reference.png` from this folder as the input image.

**Run it 4 times** and show all 4 raw outputs before choosing or compositing anything.

**Prompt:**

Redraw this house as a hand-cut paper collage illustration, like layered coloured paper and card cut with scissors, with visible paper texture, slightly uneven hand-cut edges and soft shadows between the layers. Keep the composition and every element in the same place: the green pitched roof, the round cream plaque in the roof gable holding the Soil Food Web Foundation logo exactly as it is, the dark brown chimney on the right, the cream plank walls, the two round porthole windows with the microscope photos inside them unchanged, the small OPEN sign hanging over the door, the open doorway with the photo of a laughing student at a microscope inside it unchanged, the dark green door swung open to the right, and the small brown step. Colours: roof Food Web Green #156826 with a darker left side, walls warm cream, chimney and frames Soil Brown #4F3433, door deep green #22371F. Plain flat cream background #F4F1EA. Keep the logo, the window photos and the doorway photo as real photos, untouched. No text other than the logo and the word OPEN.

**After choosing one:** remove the cream background (rembg, isnet-general-use), save it as `layers/03-house-replicate.png`, and in `build.py` swap the drawn house, door, windows and sign layers for that one picture at x=250, y=500 (580 x 620 px). Then run `build.py` and `make-pptx.js` again.
