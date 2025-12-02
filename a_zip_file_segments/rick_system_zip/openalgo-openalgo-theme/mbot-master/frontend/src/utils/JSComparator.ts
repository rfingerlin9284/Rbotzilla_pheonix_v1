/* eslint-disable @typescript-eslint/no-explicit-any */

export class JSComparator {
	static isString(value: any): boolean {
		return typeof value === 'string';
	}

	static isNumber(value: any): boolean {
		return typeof value === 'number' && !isNaN(value);
	}

	static isSameTypeAndValue(value1: any, value2: any): boolean {
		return value1 === value2;
	}

	static isNotSameTypeOrValue(value1: any, value2: any): boolean {
		return value1 !== value2;
	}

	static isValue(value1: any, value2: any): boolean {
		return value1 == value2;
	}

	static isNotValue(value1: any, value2: any): boolean {
		return value1 != value2;
	}

	static isFalsy(value: any): boolean {
		return !value;
	}

	static isTruthy(value: any): boolean {
		return !!value;
	}

	static isArray(value: any): boolean {
		return Array.isArray(value);
	}

	static isNull(value: any): boolean {
		return value === null;
	}

	static isUndefined(value: any): boolean {
		return value === undefined;
	}

	static isNullOrUndefined(value: any): boolean {
		return value === null || value === undefined;
	}

	static isObject(value: any): boolean {
		return typeof value === 'object' && value !== null;
	}

	static isFunction(value: any): boolean {
		return typeof value === 'function';
	}
  
	static isEmpty(value: any): boolean {
		return (
			value == null ||
			(this.isString(value) || this.isArray(value) && value.length === 0) ||
			(this.isObject(value) && Object.keys(value).length === 0)
			);
	}
}
