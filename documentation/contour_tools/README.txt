Contour Retopology Beta READ NE

0. How do I get it?
    -TBA, invitation only for the early beta (mature alpha?)


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
    