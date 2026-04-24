import React from "react";

const Table = ({ columns, data }) => {
  return (
    <table style={styles.table}>
      <thead>
        <tr>
          {columns.map((col, index) => (
            <th key={index} style={styles.th}>
              {col}
            </th>
          ))}
        </tr>
      </thead>

      <tbody>
        {data.map((row, i) => (
          <tr key={i}>
            {columns.map((col, j) => (
              <td key={j} style={styles.td}>
                {row[col]}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
};

const styles = {
  table: {
    width: "100%",
    borderCollapse: "collapse",
    background: "#fff",
  },
  th: {
    padding: "10px",
    borderBottom: "2px solid #ddd",
    textAlign: "left",
  },
  td: {
    padding: "10px",
    borderBottom: "1px solid #eee",
  },
};

export default Table;