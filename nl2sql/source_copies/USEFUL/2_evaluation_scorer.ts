// evaluator.ts - Functions for evaluating SQL query results

import { MedTemplate } from './medTemplateLists';


/**
 * Evaluates the accuracy of SQL query results by comparing them with expected results.
 * 
 * @param template A completed MedTemplate with results to evaluate
 * @returns The same template with updated analysis.accuracy score (1-10)
 */
export function evaluateResults(template: MedTemplate): MedTemplate {
  // Make a deep copy of the template to avoid modifying the original
  const evaluatedTemplate = JSON.parse(JSON.stringify(template));
  
  // Default score if we can't evaluate
  let accuracyScore = 1;
  
  try {
    // Check if we have valid results to compare
    const actualResults = template.output.results;
    const expectedResults = template.input.expected_result_data;
    const expectedCount = template.input.expected_result_row_count;
    
    // If results is a string (error or empty), set low accuracy
    if (typeof actualResults === 'string') {
      accuracyScore = 1;
    } else if (!Array.isArray(actualResults)) {
      // If results is not an array, set low accuracy
      accuracyScore = 2;
    } else {
      // We have an array of results to evaluate
      const actualCount = actualResults.length;
      
      // Start with base score of 5
      accuracyScore = 5;
      
      // Check row count match if expected count is provided
      if (expectedCount !== null) {
        if (actualCount === expectedCount) {
          accuracyScore += 2; // Perfect count match
        } 
        else if (Math.abs(actualCount - expectedCount) <= 2) {
          accuracyScore += 1; // Close count match
        } 
        else if (actualCount === 0) {
          accuracyScore = 2; // No results when some were expected
        }
        if (actualCount === 0 && expectedCount === 0) {
          accuracyScore = 10; // Both have no results
        }
      }
      
      // Check data content match if expected data is provided
      if (Array.isArray(expectedResults) && expectedResults.length > 0) {
        // Calculate what percentage of expected fields are found in actual results
        let matchedFields = 0;
        let totalFields = 0;
        
        // For each expected result row
        for (const expectedRow of expectedResults) {
          const expectedKeys = Object.keys(expectedRow);
          totalFields += expectedKeys.length;
          
          // Try to find a matching row in actual results
          for (const actualRow of actualResults) {
            for (const key of expectedKeys) {
              if (actualRow[key] === expectedRow[key]) {
                matchedFields++;
              }
            }
          }
        }
        
        // Calculate match percentage and adjust score
        if (totalFields > 0) {
          const matchPercentage = (matchedFields / totalFields) * 100;
          
          if (matchPercentage >= 99) {
            accuracyScore = 10; // Excellent match
          } else if (matchPercentage >= 75) {
            accuracyScore = 9; // Very good match
          } else if (matchPercentage >= 60) {
            accuracyScore = 8; // Good match
          } else if (matchPercentage >= 45) {
            accuracyScore = 7; // Decent match
          } else if (matchPercentage >= 30) {
            accuracyScore = 6; // Fair match
          } else if (matchPercentage >= 15) {
            accuracyScore = 5; // Poor match
          } else {
            accuracyScore = 4; // Very poor match
          }
        }

        // Add a summary explanation for the accuracy score
        let accuracyNotes = '';
switch (accuracyScore) {
  case 10:
    accuracyNotes = `${accuracyScore}. Excellent match: >98% of expected fields matched`;
    break;
  case 9:
    accuracyNotes = `${accuracyScore}. Very good match: 75–90% of expected fields matched`;
    break;
  case 8:
    accuracyNotes = `${accuracyScore}. Good match: 60–75% of expected fields matched`;
    break;
  case 7:
    accuracyNotes = `${accuracyScore}. Decent match: 45–60% of expected fields matched`;
    break;
  case 6:
    accuracyNotes = `${accuracyScore}. Fair match: 30–45% of expected fields matched`;
    break;
  case 5:
    accuracyNotes = `${accuracyScore}. Poor match: 15–30% of expected fields matched`;
    break;
  case 4:
    accuracyNotes = `${accuracyScore}. Very poor match: <15% of expected fields matched`;
    break;
}
evaluatedTemplate.analysis.accuracy_notes = accuracyNotes;
        

      }
    }
  } catch (error) {
    console.error("Error evaluating results:", error);
    accuracyScore = 1; // Set lowest score on error
  }
  
  // Update the template with the calculated accuracy score
  evaluatedTemplate.analysis.accuracy = accuracyScore;
  
  return evaluatedTemplate;
}

/**
 * Helper function to compare two objects for equality
 * 
 * @param obj1 First object to compare
 * @param obj2 Second object to compare
 * @returns True if objects have the same properties and values
 */
function areObjectsEqual(obj1: any, obj2: any): boolean {
  if (obj1 === null || obj2 === null) return obj1 === obj2;
  if (typeof obj1 !== 'object' || typeof obj2 !== 'object') return obj1 === obj2;
  
  const keys1 = Object.keys(obj1);
  const keys2 = Object.keys(obj2);
  
  if (keys1.length !== keys2.length) return false;
  
  return keys1.every(key => 
    keys2.includes(key) && areObjectsEqual(obj1[key], obj2[key])
  );
}