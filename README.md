# Shaman
Platform that optimizes course plans for undergraduate college students.

## Optimization

The optimization model is essentially minimizing a single decision variable that each linear combination of classes per semester is set less than or equal to, all while 
satisfying a few constraints.

### Decision Variables

* sched - a shape 2 matrix built with two arrays of binary variables indexed by semester first, then each class offered second. One corresponds to the class taken at the given 
indexed semester, a zero corresponds to class not taken
* bound - a single integer decision variable that the linear combination of possible classes each semester will be set less than or equal to. Will be minimized in the 
objective function

### Constraints

* max_hour - constraint that makes sure each linear combination of classes taken is less than or equal to the given maximum hours per semester
* min_hour - constraint that makes sure each linear combination of classes taken is more than or equal to the given minimum hours per semester to remain a full-time student
* cores - constraint that ensures each core class that is necessary for graduating for your chosen degree is taken
* avai - contraint that ensures the given class is offered at the time the model recommends you take it
* prereq - constraint that ensures each class recommended by the model has followed the logical chain of prerequisites necessary 

### Objective Function

The model is minimizing the bound decision variable while modifying the bound and sched matrix variables. In English (kind of), the objective function is trying to minimize the 
hours for the semester with the most amount of hours while meeting the constraints.
