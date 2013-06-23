Contour Retopology Beta READ ME

0. How do I get it?
    -TBA, invitation only for the early beta (mature alpha?)
    -Later....TBA


I. What is it for?
    -quad retopo of surfaces which have a closed loop
     cross section in certain regions
     eg.  (tubes, tails, limbs, ears, appendages)

    -quad retopo of open surfaces


II. How do I use it?

    0.  Iniate Operator
        -Select a mesh object in object mode

        -Select two mesh objects and enter editmode on one of them

        -Call "Contour Retopologize" from the spacebar menu
         (later add keyboard shortcut and UI button)
    

    A.  Generate cuts

       -Left click and drag to draw new cut lines
       -plane normal will be perpenicular to line drawn and view direction
           (for the math people... View Dir x Cut Line)
       -a point on the plane will be established by raycasing the midpoint
        of the cut line onto the object.  (no wireframe view)

       -new cuts can be drawn in pretty much any order.  The operator
        does its best to infer the appropriate order of the cuts

    B.  Altering Cuts

        -Left click and drag to tranlate Cut Line

        -Left click and drag the ends of cut line to
         rotate the normal around the view direction (kind of)

        -Left click

    C.  Remove Cuts
        -Right click on the blue line in the "Cut Line" widget
        -Left click and drag the cut line off the mesh



    D.  Altering number of "Follows"
        -Hold 'ctrl + scrollwheel" to alter
        -for on scroll wheel, holt "ctrl" and use up arrow.


    E.  Improving mesh quality

        o.  Note, only available on cyclic loops

        i.  Manually
            -Disable"Iterative Alignment" in the addon preferences
            -Hover mouse over a cutline widget and use left/right arrow
             to shift vert distribution along the cutline

        ii.  Automatically
            -Enable "Iterative Alignment" in the addon preferences
            -a cutline must be altered in some way...eg, slight translate
             or angle change to get the mesh to refresh

    F.  Extending existing geometry.

        -Be in editmode on your "retopo" mesh with the original object
         also selected.

        -select the geometry to extend

        -draw new geometry (preview will not show connection...TO DO)

        -Geometry will be bridged after completion of operator.



    G.  Finish

        -Hit enter or numpad return to confirm cuts and add new
         geomtry to the retopo mesh or create new retopo object.


III.  Where do I report bugs?



IV.  Where do I make suggestions for improvement?



V.   What's the best way to get my suggestions
     implemented of bugs fixed the fastest?
     0.  Make sure the suggestion or bug isn't already being
         considered or discussed by...

        i. checking the existing bugs/feature requests
       ii. browsing the BA thread here:

     A.  Clear demonstration

        i.  for bugs...
            a) a .blend file
            b) a screen shot
            c) a copy of the error or a screenshot of the error

        ii.  for feature requests or behavioral improvements
            a) a blend file with current result and manual desired result
            b) screenshots substitue for a)
            C) screenshots of mockups for behavioral or visual improvements
            d) design doc proposal

     B.  $$

     C.  Code review
    