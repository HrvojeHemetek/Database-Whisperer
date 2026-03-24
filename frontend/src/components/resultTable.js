import React from 'react';
import '../css/resultTable.css';

const ResultTable = ({ result }) => {
  // Get the column headers
  const columns = Object.keys(result);

  // Get the row indices
  const rowIndices = Object.keys(result[columns[0]]);

  return (
    <div className="table-wrapper">
      <table className="table-container">
        <thead>
          <tr>
            {columns.map(column => (
              <th key={column}>{column}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rowIndices.map(rowIndex => (
            <tr key={rowIndex}>
              {columns.map(column => (
                <td key={column + rowIndex}>{result[column][rowIndex]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ResultTable;
