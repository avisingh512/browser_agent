import React, { useState } from 'react';

const CompleteForm = () => {
  const [formData, setFormData] = useState({
    text: '',
    email: '',
    password: '',
    number: '',
    tel: '',
    url: '',
    date: '',
    time: '',
    datetime: '',
    month: '',
    week: '',
    color: '#000000',
    range: '50',
    file: null,
    search: '',
    checkbox: false,
    radio: 'option1',
    select: '',
    multiselect: [],
    textarea: '',
    // New dynamic field
    extraInfo: ''
  });

  const selectOptions = ['Credit Card', 'PayPal', 'Bank Transfer'];
  const multiSelectOptions = ['Feature 1', 'Feature 2', 'Feature 3', 'Feature 4'];
  const radioOptions = ['option1', 'option2', 'option3'];

  const handleChange = (e) => {
    const { name, value, type, checked, files } = e.target;
    
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked :
              type === 'file' ? files[0] :
              type === 'select-multiple' ? Array.from(e.target.selectedOptions, option => option.value) :
              value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Form submitted:', formData);
    alert('Form submitted successfully!');
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow">
      <h2 className="text-2xl font-bold mb-6">Complete Form Demo</h2>
      
      <form id="myForm" onSubmit={handleSubmit} className="space-y-6">
        {/* Text Input */}
        <div className="form-group">
          <label htmlFor="text">Text:</label>
          <input
            type="text"
            id="text"
            name="text"
            data-testid="text-input"
            value={formData.text}
            onChange={handleChange}
            className="form-control w-full p-2 border rounded"
          />
        </div>

        {/* Email Input */}
        <div className="form-group">
          <label htmlFor="email">Email:</label>
          <input
            type="email"
            id="email"
            name="email"
            data-testid="email-input"
            value={formData.email}
            onChange={handleChange}
            className="form-control w-full p-2 border rounded"
          />
        </div>

        {/* Password Input */}
        <div className="form-group">
          <label htmlFor="password">Password:</label>
          <input
            type="password"
            id="password"
            name="password"
            data-testid="password-input"
            value={formData.password}
            onChange={handleChange}
            className="form-control w-full p-2 border rounded"
          />
        </div>

        {/* Number Input */}
        <div className="form-group">
          <label htmlFor="number">Number:</label>
          <input
            type="number"
            id="number"
            name="number"
            data-testid="number-input"
            value={formData.number}
            onChange={handleChange}
            className="form-control w-full p-2 border rounded"
          />
        </div>

        {/* Telephone Input */}
        <div className="form-group">
          <label htmlFor="tel">Telephone:</label>
          <input
            type="tel"
            id="tel"
            name="tel"
            data-testid="tel-input"
            value={formData.tel}
            onChange={handleChange}
            className="form-control w-full p-2 border rounded"
          />
        </div>

        {/* URL Input */}
        <div className="form-group">
          <label htmlFor="url">URL:</label>
          <input
            type="url"
            id="url"
            name="url"
            data-testid="url-input"
            value={formData.url}
            onChange={handleChange}
            className="form-control w-full p-2 border rounded"
          />
        </div>

        {/* Date Input */}
        <div className="form-group">
          <label htmlFor="date">Date:</label>
          <input
            type="date"
            id="date"
            name="date"
            data-testid="date-input"
            value={formData.date}
            onChange={handleChange}
            className="form-control w-full p-2 border rounded"
          />
        </div>

        {/* Time Input */}
        <div className="form-group">
          <label htmlFor="time">Time:</label>
          <input
            type="time"
            id="time"
            name="time"
            data-testid="time-input"
            value={formData.time}
            onChange={handleChange}
            className="form-control w-full p-2 border rounded"
          />
        </div>

        {/* DateTime Input */}
        <div className="form-group">
          <label htmlFor="datetime">DateTime:</label>
          <input
            type="datetime-local"
            id="datetime"
            name="datetime"
            data-testid="datetime-input"
            value={formData.datetime}
            onChange={handleChange}
            className="form-control w-full p-2 border rounded"
          />
        </div>

        {/* Month Input */}
        <div className="form-group">
          <label htmlFor="month">Month:</label>
          <input
            type="month"
            id="month"
            name="month"
            data-testid="month-input"
            value={formData.month}
            onChange={handleChange}
            className="form-control w-full p-2 border rounded"
          />
        </div>

        {/* Week Input */}
        <div className="form-group">
          <label htmlFor="week">Week:</label>
          <input
            type="week"
            id="week"
            name="week"
            data-testid="week-input"
            value={formData.week}
            onChange={handleChange}
            className="form-control w-full p-2 border rounded"
          />
        </div>

        {/* Color Input */}
        <div className="form-group">
          <label htmlFor="color">Color:</label>
          <input
            type="color"
            id="color"
            name="color"
            data-testid="color-input"
            value={formData.color}
            onChange={handleChange}
            className="form-control w-20 p-1 border rounded"
          />
        </div>

        {/* Range Input */}
        <div className="form-group">
          <label htmlFor="range">Range ({formData.range}):</label>
          <input
            type="range"
            id="range"
            name="range"
            data-testid="range-input"
            min="0"
            max="100"
            value={formData.range}
            onChange={handleChange}
            className="form-control w-full"
          />
        </div>

        {/* File Input */}
        <div className="form-group">
          <label htmlFor="file">File:</label>
          <input
            type="file"
            id="file"
            name="file"
            data-testid="file-input"
            onChange={handleChange}
            className="form-control w-full p-2 border rounded"
          />
        </div>

        {/* Search Input */}
        <div className="form-group">
          <label htmlFor="search">Search:</label>
          <input
            type="search"
            id="search"
            name="search"
            data-testid="search-input"
            value={formData.search}
            onChange={handleChange}
            className="form-control w-full p-2 border rounded"
          />
        </div>

        {/* Checkbox with Dynamic Field */}
        <div className="form-group">
          <label className="flex items-center">
            <input
              type="checkbox"
              id="checkbox"
              name="checkbox"
              data-testid="checkbox-input"
              checked={formData.checkbox}
              onChange={handleChange}
              className="mr-2"
            />
            <span>I agree to terms (triggers extra field)</span>
          </label>
        </div>

        {/* Dynamic Extra Info Field - Appears when checkbox is checked */}
        {formData.checkbox && (
          <div className="form-group">
            <label htmlFor="extraInfo">Extra Information (if agreed):</label>
            <input
              type="text"
              id="extraInfo"
              name="extraInfo"
              data-testid="extraInfo-input"
              value={formData.extraInfo}
              onChange={handleChange}
              className="form-control w-full p-2 border rounded"
            />
          </div>
        )}

        {/* Radio Buttons */}
        <div className="form-group">
          <label className="block mb-2">Radio Options:</label>
          {radioOptions.map(option => (
            <label key={option} className="flex items-center mb-2">
              <input
                type="radio"
                name="radio"
                value={option}
                data-testid={`radio-${option}`}
                checked={formData.radio === option}
                onChange={handleChange}
                className="mr-2"
              />
              <span>{option}</span>
            </label>
          ))}
        </div>

        {/* Select Dropdown */}
        <div className="form-group">
          <label htmlFor="select">Payment Method:</label>
          <select
            id="select"
            name="select"
            data-testid="select-input"
            value={formData.select}
            onChange={handleChange}
            className="form-control w-full p-2 border rounded"
          >
            <option value="">Select payment method</option>
            {selectOptions.map(option => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </div>

        {/* Multi-Select */}
        <div className="form-group">
          <label htmlFor="multiselect">Features (Multi-Select):</label>
          <select
            id="multiselect"
            name="multiselect"
            data-testid="multiselect-input"
            multiple
            value={formData.multiselect}
            onChange={handleChange}
            className="form-control w-full p-2 border rounded"
            size="4"
          >
            {multiSelectOptions.map(option => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </div>

        {/* Textarea */}
        <div className="form-group">
          <label htmlFor="textarea">Comments:</label>
          <textarea
            id="textarea"
            name="textarea"
            data-testid="textarea-input"
            value={formData.textarea}
            onChange={handleChange}
            className="form-control w-full p-2 border rounded"
            rows="4"
          />
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          data-testid="submit-button"
          className="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600"
        >
          Submit
        </button>
      </form>
    </div>
  );
};

export default CompleteForm;