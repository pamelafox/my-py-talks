/*
 * highlight.js terraform syntax highlighting definition
 *
 * @see https://github.com/highlightjs/highlight.js
 *
 * :TODO:
 *
 * @package: highlightjs-terraform
 * @author:  Nikos Tsirmirakis <nikos.tsirmirakis@winopsdba.com>
 * @since:   2019-03-20
 *
 * Description: Terraform (HCL) language definition
 * Category: scripting
 */

var module = module ? module : {};     // shim for browser use

function hljsDefineBicep(hljs) {
	var NUMBERS = {
		className: 'number',
		begin: '\\b\\d+(\\.\\d+)?',
		relevance: 0
	};
	var STRINGS = {
		className: 'string',
		begin: '\'',
		end: '\'',
		contains: [{
			className: 'variable',
			begin: '\\${',
			end: '\\}',
			relevance: 9,
			contains: [{
				className: 'string',
				begin: '"',
				end: '"'
			}, {
			className: 'meta',
			begin: '[A-Za-z_0-9]*' + '\\(',
			end: '\\)',
			contains: [
				NUMBERS, {
					className: 'string',
					begin: '"',
					end: '"',
					contains: [{
						className: 'variable',
						begin: '\\${',
						end: '\\}',
						contains: [{
							className: 'string',
							begin: '"',
							end: '"',
							contains: [{
								className: 'variable',
								begin: '\\${',
								end: '\\}'
							}]
						}, {
							className: 'meta',
							begin: '[A-Za-z_0-9]*' + '\\(',
							end: '\\)'
						}]
					}]
          		},
          	'self']
			}]
		}]
	};

    return {
        keywords: 'metadata targetScope resource module param var output for in if existing import as type with using',
        literal: 'false true null',
        contains: [
            hljs.COMMENT('\\#', '$'),
            NUMBERS,
            STRINGS
        ]
    }
}

module.exports = function(hljs) {
    hljs.registerLanguage('bicep', hljsDefineBicep);
};

module.exports.definer = hljsDefineBicep;