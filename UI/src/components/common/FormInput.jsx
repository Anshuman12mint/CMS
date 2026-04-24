import React from "react";

const FormInput = ({
  label,
  value,
  onChange,
  type = "text",
  placeholder,
}) => {
  return (
    <div style={styles.container}>
      {label && <label style={styles.label}>{label}</label>}
      <input
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        style={styles.input}
      />
    </div>
  );
};

const styles = {
  container: {
    marginBottom: "10px",
  },
  label: {
    display: "block",
    marginBottom: "4px",
    fontWeight: "bold",
  },
  input: {
    width: "100%",
    padding: "10px",
    borderRadius: "5px",
    border: "1px solid #ccc",
  },
};

export default FormInput;